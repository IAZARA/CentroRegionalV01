from app import db
from datetime import datetime

class NewsLocation(db.Model):
    __tablename__ = 'news_locations'

    id = db.Column(db.Integer, primary_key=True)
    news_id = db.Column(db.Integer, db.ForeignKey('news.id'), nullable=False)
    location_name = db.Column(db.String(255), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    country_code = db.Column(db.String(2))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación con la noticia
    news = db.relationship('News', backref=db.backref('locations', lazy=True))

    def __init__(self, news_id, location_name, latitude, longitude, country_code=None):
        self.news_id = news_id
        self.location_name = location_name
        self.latitude = latitude
        self.longitude = longitude
        self.country_code = country_code

    def to_dict(self):
        return {
            'id': self.id,
            'news_id': self.news_id,
            'location_name': self.location_name,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'country_code': self.country_code,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<NewsLocation {self.location_name} ({self.latitude}, {self.longitude})>'
