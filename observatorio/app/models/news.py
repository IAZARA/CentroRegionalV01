from app import db
from datetime import datetime

class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    content = db.Column(db.Text)
    url = db.Column(db.String(1000), unique=True, nullable=False)
    source = db.Column(db.String(200))
    country = db.Column(db.String(100))
    published_date = db.Column(db.DateTime)
    image_url = db.Column(db.String(1000))
    keywords = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<News {self.title}>'
    
    @property
    def summary(self):
        """Retorna un resumen del contenido limitado a 200 caracteres"""
        if self.content:
            return self.content[:200] + '...' if len(self.content) > 200 else self.content
        return ''

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'url': self.url,
            'source': self.source,
            'country': self.country,
            'published_date': self.published_date.isoformat() if self.published_date else None,
            'image_url': self.image_url,
            'keywords': self.keywords,
            'created_at': self.created_at.isoformat()
        }
