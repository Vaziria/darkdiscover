from typing import List
from common.logger import Logger

from .client import Client
from .tag import TagRepo
from .category import CategoryRepo
from .post import PostRepo

logger = Logger(__name__)

class Site:
    siteid: int
    client: Client
    tagRepo: TagRepo
    categRepo: CategoryRepo
    postRepo: PostRepo
    url: str

    def __init__(self, siteid: int, url: str, client: Client):
        self.siteid = siteid
        self.url = url
        self.client = client

        self.tagRepo = TagRepo(client, self.siteid)
        self.categRepo = CategoryRepo(client, self.siteid)
        self.postRepo = PostRepo(client, self.siteid, self.url, self.tagRepo, self.categRepo)


class SiteRepo:
    client: Client

    def __init__(self, client: Client):
        self.client = client

    def parse_site(self, site) -> Site:
        url = site['URL']
        site_obj = Site(site['ID'], url, self.client)
        return site_obj

    def get_sites(self) -> List[Site]:
        path = "https://public-api.wordpress.com/rest/v1.2/me/sites"
        query = {
            "http_envelope": 1,
            "site_visibility": "all",
            "include_domain_only": "true",
            "site_activity": "active",
            "fields": "ID,URL,capabilities,icon,is_multisite,is_private,is_coming_soon,is_vip,jetpack,jetpack_modules,name,options,plan,products,single_user_site,visible,lang,launch_status,site_migration,is_fse_active,is_fse_eligible,is_core_site_editor_enabled,is_wpcom_atomic,description&options=admin_url,advanced_seo_front_page_description,advanced_seo_title_formats,allowed_file_types,anchor_podcast,created_at,default_comment_status,default_ping_status,default_post_format,design_type,frame_nonce,gmt_offset,has_pending_automated_transfer,is_automated_transfer,is_cloud_eligible,is_domain_only,is_mapped_domain,is_redirect,is_wpcom_atomic,is_wpcom_store,is_wpforteams_site,p2_hub_blog_id,woocommerce_is_active,jetpack_frame_nonce,jetpack_version,main_network_site,page_on_front,page_for_posts,podcasting_archive,podcasting_category_id,publicize_permanently_disabled,show_on_front,site_segment,software_version,timezone,upgraded_filetypes_enabled,unmapped_url,verification_services_codes,videopress_enabled,woocommerce_is_active,wordads,site_creation_flow"
        }

        headers = {
            'referer': 'https://public-api.wordpress.com/wp-admin/rest-proxy/?v=2.0'
        }

        res = self.client.session.get(path, query=query, headers=headers)

        if res.ok:
            hasil = []
            for site in res.json()['body']['sites']:
                site = self.parse_site(site)
                hasil.append(site)

            return hasil
        
        raise Exception('error tidak bisa ambil site')

if __name__ == '__main__':
    client = Client("manorder123@gmail.com", "santoso7777")
    client.login()

    repo = SiteRepo(client)
    hasil = repo.get_sites()
    print(hasil)
