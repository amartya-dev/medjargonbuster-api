import app
from app.extractor.base import BaseExtractor, detect_content_type

import logging


log = logging.getLogger(__name__)


from app.models import ExtractorRequest, ExtractorResponse


# newspaper - can extract html-based websites
from newspaper import Article, Config


class WebArticleExtractor(BaseExtractor):
    """
    Uses newspaper3k library to scrape web (news) articles.
    See quickstart: https://newspaper.readthedocs.io/en/latest/user_guide/quickstart.html

    """

    def can_handle(self, request: ExtractorRequest) -> bool:
        # we handle only html content types by URL
        return request.url and "html" in detect_content_type(request.url)

    def extract(self, request: ExtractorRequest) -> ExtractorResponse:
        try:
            user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
            config = Config()
            config.browser_user_agent = user_agent
            article = Article(
                request.url, keep_article_html=True, fetch_images=False, config=config
            )
            article.download()
            article.parse()
            # article.nlp()

            text = article.text
            meta = {
                "source": "web_article",
                "source_url": article.source_url,
                "article_html": article.article_html,
                "title": article.title,
                "top_image": article.top_image,
                "images": article.images,
                "videos": article.movies,
                "meta_language": article.meta_lang,
                "meta_keywords": article.meta_keywords,
                "authors": article.authors,
                "publish_date": article.publish_date,
            }
            # construct response
            response = ExtractorResponse(meta=meta, text=text or "")
        except Exception as e:
            msg = f"Error using newspaper3k extractor: {str(e)}"
            log.error(msg)
            response = ExtractorResponse(error=msg)

        return response