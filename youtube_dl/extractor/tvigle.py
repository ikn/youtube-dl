# encoding: utf-8
from __future__ import unicode_literals

import re

from .common import InfoExtractor
from ..utils import (
    float_or_none,
    int_or_none,
    parse_age_limit,
)


class TvigleIE(InfoExtractor):
    IE_NAME = 'tvigle'
    IE_DESC = 'Интернет-телевидение Tvigle.ru'
    _VALID_URL = r'https?://(?:www\.)?(?:tvigle\.ru/(?:[^/]+/)+(?P<display_id>[^/]+)/$|cloud\.tvigle\.ru/video/(?P<id>\d+))'

    _TESTS = [
        {
            'url': 'http://www.tvigle.ru/video/sokrat/',
            'md5': '36514aed3657d4f70b4b2cef8eb520cd',
            'info_dict': {
                'id': '1848932',
                'display_id': 'sokrat',
                'ext': 'flv',
                'title': 'Сократ',
                'description': 'md5:d6b92ffb7217b4b8ebad2e7665253c17',
                'duration': 6586,
                'age_limit': 12,
            },
        },
        {
            'url': 'http://www.tvigle.ru/video/vladimir-vysotskii/vedushchii-teleprogrammy-60-minut-ssha-o-vladimire-vysotskom/',
            'md5': 'e7efe5350dd5011d0de6550b53c3ba7b',
            'info_dict': {
                'id': '5142516',
                'ext': 'flv',
                'title': 'Ведущий телепрограммы «60 минут» (США) о Владимире Высоцком',
                'description': 'md5:027f7dc872948f14c96d19b4178428a4',
                'duration': 186.080,
                'age_limit': 0,
            },
        }, {
            'url': 'https://cloud.tvigle.ru/video/5267604/',
            'only_matching': True,
        }
    ]

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        video_id = mobj.group('id')
        display_id = mobj.group('display_id')

        if not video_id:
            webpage = self._download_webpage(url, display_id)
            video_id = self._html_search_regex(
                r'class="video-preview current_playing" id="(\d+)">',
                webpage, 'video id')

        video_data = self._download_json(
            'http://cloud.tvigle.ru/api/play/video/%s/' % video_id, display_id)

        item = video_data['playlist']['items'][0]

        title = item['title']
        description = item.get('description')
        thumbnail = item.get('thumbnail')
        duration = float_or_none(item.get('durationMilliseconds'), 1000)
        age_limit = parse_age_limit(item.get('ageRestrictions'))

        formats = []
        for vcodec, fmts in item['videos'].items():
            for format_id, video_url in fmts.items():
                if format_id == 'm3u8':
                    formats.extend(self._extract_m3u8_formats(
                        video_url, video_id, 'mp4', m3u8_id=vcodec))
                    continue
                height = self._search_regex(
                    r'^(\d+)[pP]$', format_id, 'height', default=None)
                formats.append({
                    'url': video_url,
                    'format_id': '%s-%s' % (vcodec, format_id),
                    'vcodec': vcodec,
                    'height': int_or_none(height),
                    'filesize': int_or_none(item.get('video_files_size', {}).get(vcodec, {}).get(format_id)),
                })
        self._sort_formats(formats)

        return {
            'id': video_id,
            'display_id': display_id,
            'title': title,
            'description': description,
            'thumbnail': thumbnail,
            'duration': duration,
            'age_limit': age_limit,
            'formats': formats,
        }
