import re
import urllib.parse


class Convertiser:
    def get_url(self, base_url: str, epi: str, deep_link: str):
        # Define the pattern for 32 alphanumeric characters, underscores, and hyphens
        pattern = re.compile(r'^[a-zA-Z0-9_-]{32}$')
        if not bool(pattern.match(epi)):
            raise ValueError(f'EPI: {epi} does not follow the pattern')

        if base_url[-1] != '/':
            base_url += '/'

        encoded_deep_link = urllib.parse.quote(deep_link, safe='')
        return f'{base_url}?deep_link={encoded_deep_link}&sid={epi}'


class Tradedoubler:
    def get_url(self, base_url: str, epi: str, deep_link: str):
        encoded_deep_link = urllib.parse.quote(deep_link, safe='')
        return f"{base_url}&epi={epi}&url={encoded_deep_link}"
