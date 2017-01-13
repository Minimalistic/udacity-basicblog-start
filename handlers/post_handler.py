from file_helpers import *
from blog_handler import BlogHandler
from models.ArticleModel import Article


class PostHandler(BlogHandler):
    def get(self, id):
        article = Article.get_by_id(int(id))
        comments = db.GqlQuery("SELECT * FROM Comment WHERE article_id=" +
                               str(int(id)) + " ORDER BY created DESC")
        if article is None:
            self.redirect('/')
        else:
            self.render("post.html",
                        isLoggedIn=self.isLoggedIn(),
                        article=article,
                        comments=comments)
