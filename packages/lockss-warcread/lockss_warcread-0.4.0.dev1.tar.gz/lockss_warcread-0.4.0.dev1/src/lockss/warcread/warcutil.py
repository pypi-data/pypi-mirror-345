#!/usr/bin/env python3

# Copyright (c) 2000-2025, Board of Trustees of Leland Stanford Jr. University
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors
# may be used to endorse or promote products derived from this software without
# specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import cgi
import gzip
from html.parser import HTMLParser
import io
from datetime import datetime
import os
from pathlib import Path
import re
import sys
import warcio
import xml.dom.minidom
from xml.etree.ElementTree import Element, SubElement, tostring as ETtostring
import xml.sax.saxutils

#
ONIX3_DATE_FORMAT = '%Y%m%dT%H%M%S'

WARC_DATE = 'WARC-Date'
WARC_URL = 'WARC-Target-URI'

class WarcRecord(object):
  '''
  An abstraction around warcio.recordloader.ArcWarcRecord.
  '''

  # Four constant keys for the dictionary returned by get_http_headers()
  HTTP_STATUS = '$status'
  HTTP_PROTOCOL = '$protocol'
  HTTP_CODE = '$code'
  HTTP_REASON = '$reason'

  # Four constants for the five types of WARC records
  TYPE_METADATA = 'metadata'
  TYPE_REQUEST = 'request'
  TYPE_RESPONSE = 'response'
  TYPE_REVISIT = 'revisit'
  TYPE_WARCINFO = 'warcinfo'

  def __init__(self, raw_warc_record):
    '''
    Constructor.

    Arguments:
    - raw_warc_record (of type warcio.recordloader.ArcWarcRecord): a WARC
    record as returned by the warcio library.
    '''
    super().__init__()
    self.__raw_warc_record = raw_warc_record
    self.__http_headers = None
    self.__http_payload = None

  def get_warc_header(self):
    '''Deprecated name of get_warc_headers().'''
    raise NotImplementedError('get_warc_header() is deprecated, use get_warc_headers()')

  def get_warc_headers(self):
    '''Retrieves this Warc record's Warc headers as a Python dict.'''
    return dict(self.get_raw_warc_record().rec_headers.headers)

  def get_http_header(self):
    '''Deprecated name of get_http_headers().'''
    raise NotImplementedError('get_http_header() is deprecated, use get_http_headers()')

  def get_http_headers(self):
    '''
    If is_response() is True, retrieves this WARC record's HTTP headers. The
    result is a dictionary with each HTTP key-value pair, as well as a mapping
    from WarcRecord.HTTP_STATUS to the HTTP status line, and from
    WarcRecord.HTTP_PROTOCOL, WarcRecord.HTTP_CODE and WarcRecord.HTTP_REASON
    to the protocol (e.g. 'HTTP/1.1'), code (integer, e.g. 404) and reason
    (e.g. 'Not Found') components thereof respectively.

    Raises:
    - RuntimeError if is_response() is False.

    See:
    - is_response()
    - get_http_status()
    - get_http_protocol()
    - get_http_code()
    - get_http_reason()
    '''
    self.__ensure_response()
    if self.__http_headers is None:
      raw = self.get_raw_warc_record()
      headers = dict(raw.http_headers.headers)
      headers[WarcRecord.HTTP_PROTOCOL] = raw.http_headers.protocol
      code, sep, reason = raw.http_headers.statusline.partition(' ')
      headers[WarcRecord.HTTP_CODE] = int(code)
      headers[WarcRecord.HTTP_REASON] = reason
      headers[WarcRecord.HTTP_STATUS] = f'{headers[WarcRecord.HTTP_PROTOCOL]} {headers[WarcRecord.HTTP_CODE]} {headers[WarcRecord.HTTP_REASON]}'
      self.__http_headers = headers
    return self.__http_headers      

  def get_http_status(self):
    '''
    If is_response() is True, retrieves this WARC record's HTTP status, for
    example 'HTTP/1.1 404 Not Found'. Convenience call for:
        rec.get_http_headers().get(WarcRecord.HTTP_STATUS)

    Raises:
    - RuntimeError if is_response() is False.

    See:
    - get_http_headers()
    - is_response()
    - WarcRecord.HTTP_STATUS
    '''
    return self.get_http_headers().get(WarcRecord.HTTP_STATUS)

  def get_http_protocol(self):
    '''
    If is_response() is True, retrieves this WARC record's HTTP status, for
    example 'HTTP/1.1'. Convenience call for:
        rec.get_http_headers().get(WarcRecord.HTTP_PROTOCOL)

    Raises:
    - RuntimeError if is_response() is False.

    See:
    - get_http_headers()
    - is_response()
    - WarcRecord.HTTP_PROTOCOL
    '''
    return self.get_http_headers().get(WarcRecord.HTTP_PROTOCOL)

  def get_http_code(self):
    '''
    If is_response() is True, retrieves this WARC record's integer HTTP code,
    for example 404. Convenience call for:
        rec.get_http_headers().get(WarcRecord.HTTP_CODE)

    Raises:
    - RuntimeError if is_response() is False.

    See:
    - get_http_headers()
    - is_response()
    - WarcRecord.HTTP_CODE
    '''
    return self.get_http_headers().get(WarcRecord.HTTP_CODE)

  def get_http_reason(self):
    '''
    If is_response() is True, retrieves this WARC record's HTTP reason, for
    example 'Not Found'. Convenience call for:
        rec.get_http_headers().get(WarcRecord.TYPE_RESPONSE)

    Raises:
    - RuntimeError if this WARC record is not of type WarcRecord.TYPE_RESPONSE

    See:
    - get_http_headers()
    - is_response()
    - WarcRecord.HTTP_REASON
    '''
    return self.get_http_headers().get(WarcRecord.HTTP_REASON)

  def get_http_payload(self, remember=False, universal_newline=False):
    '''
    Retrieves an iterable version of this WARC record's HTTP payload (if it is
    of type WarcRecord.TYPE_RESPONSE). This will throw away the eventual result
    and raise RuntimeError if called more than once, unless the first call is
    with the 'remember' argument set to True, in which case the payload will be kept in
    memory.

    Arguments:
    - remember (boolean): whether to keep the eventual result in memory for
    future calls to this method (default: False)
    - universal_newline (boolean): whether to consider not just '\n' but also
    '\r\n' and '\r' as newlines (default: False)

    Raises:
    - RuntimeError if this WARC record is not of type WarcRecord.TYPE_RESPONSE
    or if this method is called more than once without the first call with a
    'remember' argument set to True
    '''
    self.__ensure_response()
    bio = self.__http_payload
    if bio is None:
        bio = io.BytesIO()
        bio.close = lambda slf: None # io.TextIOWrapper closes the underlying buffer
        strm = self.get_raw_warc_record().content_stream()
        chunk = strm.read(1024)
        while len(chunk) > 0:
            bio.write(chunk)
            chunk = strm.read(1024)
        if remember:
            self.__http_payload = bio
    bio.seek(0)
    enc = cgi.parse_header(self.get_http_headers().get('Content-Type', ''))[1].get('charset', 'utf-8')
    return io.TextIOWrapper(bio,
                            encoding=enc,
                            newline=(None if universal_newline else ''))
    
  def get_binary_http_payload(self):
    self.__ensure_response()
    return self.get_raw_warc_record().raw_stream
    
  def get_raw_warc_record(self):
    '''Retrieves the underlying WARC record object (of type warc.WARCRecord).'''
    return self.__raw_warc_record

  def get_date(self):
    '''Retrieves the date from the Warc header.'''
    return self.get_raw_warc_record().rec_headers.get(WARC_DATE)

  def get_type(self):
    '''
    Retrieves the type of this Warc record.

    See:
    - WarcRecord.TYPE_METADATA
    - WarcRecord.TYPE_REQUEST
    - WarcRecord.TYPE_RESPONSE
    - WarcRecord.TYPE_REVISIT
    - WarcRecord.TYPE_WARCINFO
    '''
    return self.get_raw_warc_record().rec_type

  def get_url(self):
    '''Retrieves the URL from the WARC header.'''
    ret = self.get_raw_warc_record().rec_headers.get(WARC_URL)
    if ret is not None and ret.startswith('<') and ret.endswith('>'):
      ret = ret[1:-1]
    return ret

  def is_response(self):
    '''
    Determines if this WARC record is a response. Convenience call for:
        rec.get_type() == WarcRecord.TYPE_RESPONSE

    See:
    - get_type()
    '''
    return self.get_type() == WarcRecord.TYPE_RESPONSE

  def __ensure_response(self):
    '''
    Raises RuntimeError if this WARC record is not a response.

    See:
    - is_response()
    '''
    if not self.is_response():
      raise RuntimeError(f'{self.get_url()}: record type "{self.get_type()}" is not "{WarcRecord.TYPE_RESPONSE}"')

def xml_escape(st):
  '''
  Replaces less-than, greater-than and ampersand with XML escapes in the given
  string.

  Arguments:
  - st (string): the string to escape
  '''
  return xml.sax.saxutils.escape(st).encode('ascii', 'xmlcharrefreplace')

# Regular expression to identify HTML (XML, really) numeric escapes
_RE_HTML_UNESCAPE = re.compile(r'&#(x)?(\d+);', re.IGNORECASE)

def _re_html_unescape_func(m):
  '''
  Private method to be used in a regular expression substitution with
  _RE_HTML_UNESCAPE.
  '''
  if m.group(1) is None: return chr(int(m.group(2), base=10))
  else: return chr(int(m.group(2), base=16))

def html_unescape(st):
  '''
  Attempts to unescape a raw HTML string by converting non-numeric and
  numeric escapes into appropriate characters.
  
  Arguments:
  - st (string): a raw HTML string
  
  See:
  _RE_HTML_UNESCAPE
  '''
  if st is None: return None
  # Non-numeric entities (from https://wiki.python.org/moin/EscapingHtml)
  p = HTMLParser(None)
  p.save_bgn()
  p.feed(st)
  ret = p.save_end()
  # Numeric entities
  return _RE_HTML_UNESCAPE.sub(_re_html_unescape_func, ret)

def open_warc(fstr):
  '''
  Opens a Gzipped WARC file for reading and returns an instance of type
  warc.WARCFile (from the Internet Archive's warc module, which must be on the
  PYTHONPATH).

  A warc.WARCFile can be seen as a sequence of WARC records of type
  warc.WARCRecord, which consist of the following fields:
  - checksum (string): value of the WARC-Payload-Digest header
  - date (string): value of the WARC-Date header
  - header (of type warc.WARCHeader): the Warc header
  - ip_address (string): value of the WARC-IP-Address header
  - payload (file-like object): the Warc payload
  - type (string): value of the WARC-Type header
  - url (string): value of the WARC-Target-URI header
  There is also a field called offset, that should return the offset of the
  record in the WARC file, but is not currently implemented/populated. The
  warc.WARCFile instance has a close() method that should be called at the end
  of processing.

  A warc.WARCHeader can be seen as a case-insensitive dictionary, and contains
  the following fields:
  - content_length (integer): value of the Content-Length header
  - date (string): value of the WARC-Date header
  - record_id (string): value of the WARC-Record-ID header
  - type (string): value of the WARC-Type header

  Arguments:
  - fstr (string): a file path

  See:
  - https://github.com/internetarchive/warc
  - browse_records()
  - browse_responses()
  '''
  strm = Path(fstr).open('rb')
  return warcio.archiveiterator.ArchiveIterator(strm)

def browse_records(fwarc):
  '''
  Returns an iterable object over all the WARC records in the given WARC file.
  Each iterated record is of type WarcRecord (from this module, not of Internet
  Archive's warc.WARCRecord type).

  See:
  - open_warc()
  - WarcRecord
  '''
  for raw_warc_record in fwarc:
    yield WarcRecord(raw_warc_record)

def browse_responses(fwarc):
  '''
  Returns an iterable object over all the WARC records in the given WARC file
  that are of type 'response'. Each iterated record is of type WarcRecord (from
  this module, not of Internet Archive's warc.WARCRecord type).

  See:
  - open_warc()
  - WarcRecord
  '''
  for warc_record in browse_records(fwarc):
    if warc_record.is_response():
      yield warc_record

def browse_200_responses(fwarc):
  '''
  Returns an iterable object over all the WARC records in the given WARC file
  that are of type 'response' and correspond to HTTP 200. Each iterated record
  is of type WarcRecord (from this module, not of Internet Archive's
  warc.WARCRecord type).

  See:
  - open_warc()
  - WarcRecord
  '''
  for warc_record in browse_responses(fwarc):
    if warc_record.get_http_code() == 200:
      yield warc_record

class WarcProcessor(object):
  '''
  An abstract class for a WARC processor, a simplified abstraction for the
  LOCKSS daemon's concept of article iterator and metadata extractors.

  Subclasses must define concrete implementations of:
  - should_index_url()
  - should_parse_url()
  - parse_url()
  Unimplemented abstract methods will raise NotImplementedError.

  The methods of interest to subclasses are:
  - run() (main entry point for processing)
  - get_indexed_url()
  - indexed_urls()
  - emit_article()

  Other methods are there to override typical processing if needed.
  '''

  def __init__(self):
    '''Constructor.'''
    super().__init__()
    self.__indexed_urls = dict()
    self.__articles = None

  def run(self, files):
    '''
    Runs this WARC processor over the given WARC files, and returns an iterable
    of Article instances.

    Arguments:
    - files (iterable strings): names of the WARC files to be processed

    See:
    - process_files()
    - indexed_urls()
    - should_parse_url()
    - parse_url()
    '''
    self.__articles = dict()
    self.process_files(files)
    for url, record in self.indexed_urls():
      if self.should_parse_url(record):
        self.parse_url(record)
    return [art for url, art in sorted(self.__articles.items())]

  def get_indexed_url(self, url):
    '''
    Returns the WarcRecord instance currently associated with the given indexed
    URL (or None if not currently indexed).

    Arguments:
    - url (string): a URL
    '''
    return self.__indexed_urls.get(url)

  def indexed_urls(self):
    '''
    Returns an iterable object over the indexed URLs. Each iterated item is a
    tuple of the URL (string) and its associated record (of type WarcRecord).
    '''
    for url, record in self.__indexed_urls.items():
      yield url, record

  def should_index_url(self, record):
    '''
    Abstract method. Returns a boolean determining if the given URL should be
    indexed.

    Arguments:
    - record: the WARC record for the URL.
    '''
    raise NotImplementedError('should_index_url(self, record)')

  def should_parse_url(self, record):
    '''
    Abstract method. Returns a boolean determining if the given URL should be
    parsed.

    Arguments:
    - record: the WARC record for the URL.
    '''
    raise NotImplementedError('should_parse_url(self, record)')

  def parse_url(self, record):
    '''
    Abstract method. Parses the contents of a given URL and returns a dictionary
    of parsed data.

    Arguments:
    - record (of type warcutil.WarcRecord): the WARC record for the URL

    See:
    - emit_article()
    '''
    raise NotImplementedError('parse_url(self, record)')

  def process_files(self, files):
    '''
    Processes each of the given file names in turn.

    Arguments:
    - files (iterable strings): names of the WARC files to be processed

    See:
    - index_file()
    '''
    for fstr in files:
      fwarc = open_warc(fstr)
      self.index_file(fstr, fwarc)
      fwarc.close()

  def index_file(self, fstr, fwarc):
    '''
    Indexes a given Warc file.

    Arguments:
    - fstr (string): current file name
    - fwarc (file-like object): current WARC file

    See:
    - should_index_url()
    - should_parse_url()
    - select_records()
    - is_better_to_index()
    - is_parse_url_binary()
    '''
    for record in self.select_records(fstr, fwarc):
      if self.should_index_url(record):
        url = record.get_url()
        current = self.__indexed_urls.get(url)
        if self.is_better_to_index(current, record):
          self.__indexed_urls[url] = record
          if self.should_parse_url(record):
            if self.is_parse_url_binary(record):
              record.get_binary_http_payload()
            else:
              for line in record.get_http_payload(remember=True):
                  pass

  def select_records(self, fstr, fwarc):
    '''
    Returns an iterable of records to be processed inside a given WARC file. By
    default this is all response records that are HTTP 200.

    Arguments:
    - fstr (string): a file name
    - fwarc (file-like object)

    See:
    - browse_200_responses()
    '''
    return browse_200_responses(fwarc)

  def emit_article(self, article, allow_override=False):
    '''
    Emits an article during the parsing of a URL.

    Arguments:
    - article (of type Article): an article
    - allow_override (boolean, default False): whether to allow the re-emitting
    of a new article instance for a URL previously emitted (judged by the
    article's best URL)

    Raises:
    - RuntimeError if no best URL is set or if re-emitting when disallowed
    '''
    url = article.get_best_url()
    if url is None:
      raise RuntimeError(f'no article URL set: {article}')
    if not allow_override and url in self.__articles:
      raise RuntimeError(f'{url} already emitted; old {self.__articles.get(url)} vs. new {article}')
    self.__articles[url] = article

  def is_better_to_index(self, current, record):
    '''
    Returns a boolean determining if the URL instance represented by 'record'
    should be indexed instead the current one represented by 'current'. By
    default, this method gives preferences to a record with a WARC date more
    recent than the current one.

    Arguments:
    - current (of type warc.WARCRecord): WARC record currently associated with a
    URL (can be None)
    - record (of type warc.WARCRecord): other WARC record representing the same
    URL
    '''
    return current is None or current.get_date() < record.get_date()

  def is_parse_url_binary(self, record):
    return False

# A flexible regular expression for same-line HTML <meta> tags
# Group 1: one alternative for the key
# Group 2: one alternative for the key
# Group 3: one alternative for the value
# Group 4: one alternative for the value
# Group 5: one alternative for the value
# Group 6: one alternative for the value
# Group 7: one alternative for the key
# Group 8: one alternative for the key
_RE_HTML_META = re.compile('''<meta\s+(?:name=\s*(?:"([^"]*)"|'([^']*)')\s+content=\s*(?:"([^"]*)"|'([^']*)')|content=\s*(?:"([^"]*)"|'([^']*)')\s+name=\s*(?:"([^"]*)"|'([^']*)'))\s*/?>''', re.IGNORECASE)
_RE_HTML_TITLE = re.compile(r'<title[^>]*>([^<]+)</title', re.IGNORECASE)

def scrape_html_meta_tags(http_payload, encoding=None):
  '''
  Scrapes <meta> tags from an HTML page returns a dictionary mapping from each
  <meta> name attribute to a list of <meta> content attributes for that name
  (often a single item).

  Arguments:
  http_payload (file-like): an HTML page.
  encoding (None): now ignored

  See:
  _RE_HTML_META
  '''
  ret = dict()
  bigline = ''
  just_consume = False
  for line in http_payload:
    if just_consume: continue
    bigline = bigline + line
    if '<body' in line or '<BODY' in line: just_consume = True
  mat = _RE_HTML_TITLE.search(bigline)
  if mat: ret.setdefault('browsertitle', mat.group(1))
  for mat in _RE_HTML_META.finditer(bigline):
    key = mat.group(1) or mat.group(2) or mat.group(7) or mat.group(8)
    val = None
    try:
      val = (mat.group(3) or mat.group(4) or mat.group(5) or mat.group(6) or '')
    except Exception as e:
      print(f'{key}\n{e}', file=sys.stderr)
      val = 'INVALID VALUE'
    ret.setdefault(key, list()).append(val)
  return ret

def parse_endnote(http_payload, encoding=None):
  '''
  Parses an Endnote .enw file (in the form of "%X Val" lines for some tag %X and
  some value "Val"), returning a dictionary mapping from each tag to a list of
  values for that tag (often a single item).

  Arguments:
  http_payload (file-like): an Endnote file
  encoding (None): now ignored
  '''
  ret = dict()
  for line in http_payload:
    key, val = line[0:2], line[2:].strip()
    ret.setdefault(key, list()).append(val)
  return ret

class Article(object):
  '''
  A simple class to represent article data.

  This class consists of getters and setters for various typical article data
  (e.g. get_publisher(), set_publisher()), a sanity check method
  (sanity_check()), and role constants mirroring those in the daemon's
  ArticleFiles to tag arbitrary URLs.
  '''

  # Constants mirroring the daemon's ArticleFiles roles
  ROLE_ABSTRACT = 'Abstract'
  ROLE_ARTICLE_METADATA = 'ArticleMetadata'
  ROLE_CITATION = 'Citation'
  ROLE_CITATION_BIBTEX = 'CitationBibtex'
  ROLE_CITATION_ENDNOTE = 'CitationEndnote'
  ROLE_CITATION_RIS = 'CitationRis'
  ROLE_FIGURES = 'Figures'
  ROLE_FULL_TEXT_EPUB = 'FullTextEpub'
  ROLE_FULL_TEXT_HTML = 'FullTextHtml'
  ROLE_FULL_TEXT_HTML_LANDING_PAGE = 'FullTextHtmlLanding'
  ROLE_FULL_TEXT_MOBILE = 'FullTextMobile'
  ROLE_FULL_TEXT_PDF = 'FullTextPdfFile'
  ROLE_FULL_TEXT_PDF_LANDING_PAGE = 'FullTextPdfLanding'
  ROLE_FULL_TEXT_XML = 'FullTextXml'
  ROLE_ISSUE_METADATA = 'IssueMetadata'
  ROLE_REFERENCES = 'References'
  ROLE_SUPPLEMENTARY_MATERIALS = 'SupplementaryMaterials'
  ROLE_TABLES = 'Tables'

  def __init__(self, best_url=None, publisher=None, publication=None, \
      issn=None, eissn=None, volume=None, issue=None, first_page=None, \
      last_page=None, doi=None, article_title=None, isbn=None):
    '''Constructor.'''
    super().__init__()
    self._authors = list()
    self._article_title = article_title
    self._best_url = best_url
    self._date = None
    self._doi = doi
    self._eissn = eissn
    self._first_page = first_page
    self._issn = issn
    self._isbn = isbn
    self._issue = issue
    self._key_value_pairs = list()
    self._last_page = last_page
    self._publication = publication
    self._publisher = publisher
    self._volume = volume

  def sanity_check(self, \
                   article_title_required=True, \
                   date_required=False, \
                   doi_required=True,
                   isbn_required=False):
    '''
    Performs a sanity check.

    Arguments:
    - article_title_required (boolean): if True, raises ValueError if no article
    title is set (defaults to True)
    - date_required (boolean): if True, raises ValueError if no date is set
    (defaults to False).
    - doi_required (boolean): if True, raises ValueError if no DOI is set
    (defaults to True)
    - isbn_required (boolean): if True, raises ValueError if no ISBN is set
    (defaults to False).

    Raises:
    - ValueError if no best URL is set
    - ValueError if no publisher name is set
    - ValueError if no publication name is set
    - ValueError if no article title is set
    - ValueError if last page is set but first page is not set
    - ValueError if date_required is False but no date is set
    - ValueError if doi_required is True but no DOI is set
    - ValueError if isbn_required is True but no ISBN is set
    '''
    if self.get_best_url() is None:
      raise ValueError('no best URL set')
    if self.get_publisher() is None:
      raise ValueError(f'{self.get_best_url()}: no publisher name set')
    if self.get_publication() is None:
      raise ValueError(f'{self.get_best_url()}: no publication name set')
    if self.get_last_page() is not None and self.get_first_page() is None:
      raise ValueError(f'{self.get_best_url()}: last page without first page')
    if article_title_required and self.get_article_title() is None:
      raise ValueError(f'{self.get_best_url()}: no article title set')
    if date_required and self.get_date() is None:
      raise ValueError(f'{self.get_best_url()}: no date set')
    if doi_required and self.get_doi() is None:
      raise ValueError(f'{self.get_best_url()}: no DOI set')
    if isbn_required and self.get_isbn() is None:
      raise ValueError(f'{self.get_best_url()}: no ISBN set')

  def add_author(self, surname, given, prefix=None, suffix=None):
    '''
    Adds an author with the given last name, first name, optional prefix and
    optional suffix to the article's list of authors.
    '''
    self._authors.append((surname, given, prefix, suffix))

  def get_authors(self):
    '''
    Retrieves the article's list of authors as (last name, first name, prefix or
    None, suffix or None) tuples. If no authors have been added with
    add_author(), the result is an empty list (not None).
    '''
    return self._authors[:]

  def set_article_title(self, article_title):
    '''Sets the article title to the given string.'''
    self._article_title = article_title

  def get_article_title(self):
    '''Retrieves the article title.'''
    return self._article_title

  def set_best_url(self, best_url):
    '''Sets the article's best URL to the given string.'''
    self._best_url = best_url

  def get_best_url(self):
    '''Retrieves the article's best URL.'''
    return self._best_url

  def set_date(self, year, month=None, day=None):
    '''Sets the article's year, optional month and optional day strings.'''
    self._date = (year, month, day)

  def get_date(self):
    '''
    Retrieves the article's date as a (year, month or None, day or None) string
    tuple. See set_date().
    '''
    return self._date

  def set_doi(self, doi):
    '''Sets the article's DOI to the given string.'''
    self._doi = doi

  def get_doi(self):
    '''Retrieves the article's DOI.'''
    return self._doi

  def set_eissn(self, eissn):
    '''Sets the publication's eISSN to the given string.'''
    self._eissn = eissn

  def get_eissn(self):
    '''Retrieves the publication's eISSN.'''
    return self._eissn

  def set_first_page(self, first_page):
    '''Sets the article's first page to the given string.'''
    self._first_page = first_page

  def get_first_page(self):
    '''Retrieves the article's first page.'''
    return self._first_page

  def set_issn(self, issn):
    '''Sets the publication's eISSN to the given string.'''
    self._issn = issn

  def get_issn(self):
    '''Retrieves the publication's eISSN.'''
    return self._issn

  def set_isbn(self, isbn):
    '''Sets the publication's eISSN to the given string.'''
    self._isbn = isbn

  def get_isbn(self):
    '''Retrieves the publication's eISSN.'''
    return self._isbn

  def set_issue(self, issue):
    '''Sets the article's issue to the given string.'''
    self._issue = issue

  def get_issue(self):
    '''Retrieves the article's issue.'''
    return self._issue

  def add_key_value_pair(self, key, value):
    '''
    Adds the given key-value pair to the article's list of arbitrary key-value
    pairs. Keys can be repeated (Dublin Core-like).
    '''
    self._key_value_pairs.append((key, value))

  def get_key_value_pairs(self):
    '''
    Retrieves the article's list of arbitrary key-value pairs as tuples. If no
    key-value pairs have been added with add_key_value_pair(), the result is an
    empty list (not None).
    '''
    return self._key_value_pairs[:]

  def set_last_page(self, last_page):
    '''Sets the article's first page to the given string.'''
    self._last_page = last_page

  def get_last_page(self):
    '''Retrieves the article's first page.'''
    return self._last_page

  def set_publication(self, publication):
    '''Sets the article's publication name to the given string.'''
    self._publication = publication

  def get_publication(self):
    '''Retrieves the article's publication name.'''
    return self._publication

  def set_publisher(self, publisher):
    '''Sets the article's publisher name to the given string.'''
    self._publisher = publisher

  def get_publisher(self):
    '''Retrieves the article's publisher name.'''
    return self._publisher

  def set_volume(self, volume):
    '''Sets the article's volume to the given string.'''
    self._volume = volume

  def get_volume(self):
    '''Retrieves the article's volume.'''
    return self._volume

  def __repr__(self):
    return repr(self.__dict__)

def build_jats_tree(articles):
  '''
  Processes the given iterable of Article instances and builds an XML tree made
  of successive JATS 1.1 <article> nodes wrapped in a non-JATS <article-set>
  node.

  Arguments:
  - articles (iterable of Article instances): a sequence of articles

  See:
  - output_jats_tree()
  '''
  article_set_node = Element('article-set', {'date':str(datetime.utcnow())})
  for article in articles:
    article_node = SubElement(article_set_node, 'article', {'xmlns':'http://jats.nlm.nih.gov', \
                                                            'dtd-version':'1.1', \
                                                            'xmlns:xlink':'http://www.w3.org/1999/xlink'})
    front_node = SubElement(article_node, 'front')
    journal_meta_node = SubElement(front_node, 'journal-meta')
    journal_title_group_node = SubElement(journal_meta_node, 'journal-title-group')
    SubElement(journal_title_group_node, 'journal-title').text = article.get_publication()
    if article.get_issn() is not None:
      SubElement(journal_meta_node, 'issn', {'publication-format':'print'}).text = article.get_issn()
    if article.get_eissn() is not None:
      SubElement(journal_meta_node, 'issn', {'publication-format':'electronic'}).text = article.get_eissn()
    publisher_node = SubElement(journal_meta_node, 'publisher')
    SubElement(publisher_node, 'publisher-name').text = article.get_publisher()
    article_meta_node = SubElement(front_node, 'article-meta')
    if article.get_isbn() is not None:
      SubElement(article_meta_node, 'isbn', {'publication-format':'print'}).text = article.get_isbn()
    if article.get_doi() is not None:
      SubElement(article_meta_node, 'article-id', {'pub-id-type':'doi'}).text = article.get_doi()
    if article.get_article_title() is not None:
      title_group = SubElement(article_meta_node, 'title-group')
      SubElement(title_group, 'article-title').text = article.get_article_title()
    if len(article.get_authors()) > 0:
      contrib_group_node = SubElement(article_meta_node, 'contrib-group')
      for _surname, _given, _prefix, _suffix in article.get_authors():
        contrib_node = SubElement(contrib_group_node, 'contrib', {'contrib-type':'author'})
        name_node = SubElement(contrib_node, 'name')
        SubElement(name_node, 'surname').text = _surname
        SubElement(name_node, 'given-names').text = _given
        if _prefix is not None:
          SubElement(name_node, 'prefix').text = _prefix
        if _suffix is not None:
          SubElement(name_node, 'suffix').text = _suffix
    if article.get_date() is not None:
      _year, _month, _day = article.get_date()
      pub_date_node = SubElement(article_meta_node, 'pub-date', {'date-type':'pub'})
      SubElement(pub_date_node, 'year').text = _year
      if _month is not None:
        SubElement(pub_date_node, 'month').text = _month
        if _day is not None:
          SubElement(pub_date_node, 'day').text = _day
          pub_date_node.set('iso-8601-date', f'{_year}-{_month.zfill(2)}-{_day.zfill(2)}')
    if article.get_volume() is not None:
      SubElement(article_meta_node, 'volume').text = article.get_volume()
    if article.get_issue() is not None:
      SubElement(article_meta_node, 'issue').text = article.get_issue()
    if article.get_first_page() is not None:
      SubElement(article_meta_node, 'fpage').text = article.get_first_page()
      if article.get_last_page() is not None:
        SubElement(article_meta_node, 'lpage').text = article.get_last_page()
    SubElement(article_meta_node, 'self-uri', {'xlink:href':article.get_best_url()}).text = article.get_best_url()
    if len(article.get_key_value_pairs()) > 0:
      custom_meta_group_node = SubElement(article_meta_node, 'custom-meta-group')
      for _key, _value in article.get_key_value_pairs():
        custom_meta_node = SubElement(custom_meta_group_node, 'custom-meta')
        SubElement(custom_meta_node, 'meta-name').text = _key
        SubElement(custom_meta_node, 'meta-value').text = _value
  return article_set_node

def output_jats_tree(articles, fileobj=None, encoding=None):
  '''
  Processes the given iterable of Article instances and outputs an XML structure
  to the given file-like object using the given encoding. The structure is made
  of JATS 1.1 <article> nodes wrapped in a non-JATS <article-set> node. The
  textual result is one long stream; to pretty-print it, use an external
  technique, for instance piping it through xmllint -format .

  Arguments:
  - articles (iterable of Article instances): a sequence of articles
  - fileobj (file-like object): an output channel (defaults to sys.stdout)
  - encoding (None): now ignored

  See:
  - build_jats_tree()
  - http://jats.nlm.nih.gov/
  '''
  if fileobj is None:
      fileobj = sys.stdout
  #if encoding is None:
   #   encoding = 'utf-8'
  print(ETtostring(build_jats_tree(articles), encoding="unicode"), file=fileobj)

def build_onix3_tree(articles):
  '''
  Processes the given iterable of Article instances and builds an XML tree in
  ONIX for Books 3.0 format.

  Arguments:
  - articles (iterable of Article instances): a sequence of articles

  See:
  - output_onix3_tree()
  '''
  onix_message_node = Element('ONIXMessage', {'xmlns':'http://ns.editeur.org/onix/3.0/reference', \
                                              'release':'3.0'})
  header_node = SubElement(onix_message_node, 'Header')
  sender_node = SubElement(header_node, 'Sender')
  sender_name_node = SubElement(sender_node, 'SenderName')
  addressee_node = SubElement(header_node, 'Addressee')
  addressee_name_node = SubElement(addressee_node, 'AddresseeName')
  SubElement(header_node, 'SentDateTime').text = datetime.utcnow().strftime(ONIX3_DATE_FORMAT)
  first_article = True
  for article in articles:
    if first_article:
      sender_name_node.text = article.get_publisher()
      first_article = False
    product_node = SubElement(onix_message_node, 'Product')
    SubElement(product_node, 'RecordReference').text = article.get_isbn()
    SubElement(product_node, 'NotificationType').text = '03'
    product_identifier_node = SubElement(product_node, 'ProductIdentifier')
    SubElement(product_identifier_node, 'ProductIDType').text = '15' # ISBN13
    SubElement(product_identifier_node, 'IDValue').text = article.get_isbn().replace('-', '')
    if article.get_doi() is not None:
      product_identifier_node = SubElement(product_node, 'ProductIdentifier')
      SubElement(product_identifier_node, 'ProductIDType').text = '06' # DOI
      SubElement(product_identifier_node, 'IDValue').text = article.get_doi()
    product_identifier_node = SubElement(product_node, 'ProductIdentifier')
    SubElement(product_identifier_node, 'ProductIDType').text = '01' # 'Proprietary'
    SubElement(product_identifier_node, 'IDTypeName').text = 'AccessUrl'
    SubElement(product_identifier_node, 'IDValue').text = article.get_best_url()
    descriptive_detail_node = SubElement(product_node, 'DescriptiveDetail')
    SubElement(descriptive_detail_node, 'ProductComposition').text = '00' # 'Single-item retail product'
    SubElement(descriptive_detail_node, 'ProductForm').text = 'EA' # 'Digital (delivered electronically)'
    title_detail_node = SubElement(descriptive_detail_node, 'TitleDetail')
    SubElement(title_detail_node, 'TitleType').text = '01' # 'Distinctive title (book); Cover title (serial); Title on item (serial content item or reviewed resource)'
    title_element_node = SubElement(title_detail_node, 'TitleElement')
    SubElement(title_element_node, 'TitleElementLevel').text = '01' # 'Product'
    SubElement(title_element_node, 'TitleText').text = article.get_article_title()
    for author_index, author in enumerate(article.get_authors()):
      _surname, _given, _prefix, _suffix = author
      contributor_node = SubElement(descriptive_detail_node, 'Contributor')
      SubElement(contributor_node, 'SequenceNumber').text = str(author_index + 1)
      SubElement(contributor_node, 'ContributorRole').text = 'A01' # 'By (author)'
      if _prefix is not None:
        SubElement(contributor_node, 'TitlesBeforeNames').text = _prefix
      SubElement(contributor_node, 'NamesBeforeKey').text = _given
      SubElement(contributor_node, 'KeyNames').text = _surname
      if _suffix is not None:
        SubElement(contributor_node, 'SuffixToKey').text = _suffix
    publishing_detail_node = SubElement(product_node, 'PublishingDetail')
    publisher_node = SubElement(publishing_detail_node, 'Publisher')
    SubElement(publisher_node, 'PublishingRole').text = '01' # 'Publisher'
    SubElement(publisher_node, 'PublisherName').text = article.get_publisher()
    if article.get_date() is not None:
      publishing_date_node = SubElement(publishing_detail_node, 'PublishingDate')
      SubElement(publishing_date_node, 'PublishingDateRole').text = '01' # 'Publication date'
      _year, _month, _day = article.get_date()
      SubElement(publishing_date_node, 'Date').text = f'{_year}{_month or "01"}{_day or "01"}'
    copyright_statement_node = SubElement(publishing_detail_node, 'CopyrightStatement')
    SubElement(copyright_statement_node, 'CopyrightYear').text = _year
  return onix_message_node

def output_onix3_tree(articles, fileobj=None, encoding=None):
  '''
  Processes the given iterable of Article instances and outputs an XML structure
  to the given file-like object using the given encoding. The structure is an
  ONIX Books 3.0.3 <ONIXMessage> tree. The textual result is one long stream;
  to pretty-print it, use an external technique, for instance piping it through
  xmllint -format .

  Arguments:
  - articles (iterable of Article instances): a sequence of articles
  - fileobj (file-like object): an output channel (defaults to sys.stdout)
  - encoding (string): an output encoding (defaults to 'utf-8')

  See:
  - build_onix3_tree()
  '''
  if fileobj is None:
      fileobj = sys.stdout
  if encoding is None:
      encoding = 'utf-8'
  fileobj.write(ETtostring(build_onix3_tree(articles), encoding=encoding))

def run_warc_processor(warc_processor, files=None, fileobj=None, encoding=None,
                       output_type=None):
  '''
  Main entry point for WARC processor clients: automatically run the given
  WarcProcessor instances over the given sequence of WARC file names, outputting
  the XML result to the given file-like object, in the given encoding.

  Arguments:
  - files (iterable of strings): a sequence of WARC file names (defaults to all
  arguments passed to the command line invoking this)
  - articles (iterable of Article instances): a sequence of articles
  - fileobj (file-like object): an output channel (defaults to sys.stdout)
  - encoding (string): an output encoding (defaults to 'utf-8')
  - output_type (string): an output type identifier chosen among 'jats' (JATS
  article set) or 'onix3' (ONIX 3 Books); (defaults to None which defaults to
  'jats')

  Raises:
  - RuntimeError if the output type argument is invalid

  See:
  - output_jats_tree()
  - output_onix3_tree()
  '''
  if files is None:
      files = sys.argv[1:]
  if fileobj is None:
      fileobj = sys.stdout
  if encoding is None:
      encoding = 'utf-8'
  if output_type is None:
      output_type = 'jats'
  if output_type == 'jats':
    output_jats_tree(warc_processor.run(files), fileobj, encoding)
  elif output_type == 'onix3':
    output_onix3_tree(warc_processor.run(files), fileobj, encoding)
  else:
    raise RuntimeError(f'unknown output type: {output_type}')

