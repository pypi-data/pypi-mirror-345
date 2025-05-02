"""Flask extension for real-time analytics dashboards.

This module provides a Flask extension to track user behavior, API usage, and
performance metrics, with a WebSocket-powered dashboard for live updates. It
integrates with SQLAlchemy-supported databases for persistent storage.

Classes:
    AnalyticsRecord: SQLAlchemy model for storing analytics data.
    FlaskRealTimeAnalytics: Main extension class for tracking and dashboard rendering.
"""

from flask import Flask, request, render_template, make_response
from flask_socketio import SocketIO
from sqlalchemy import Column, Integer, String, Float, DateTime, func
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, UTC
from functools import wraps
import time

Base = declarative_base()


class AnalyticsRecord(Base):
    """SQLAlchemy model for storing analytics data.

    Attributes:
        id: Unique identifier for the record.
        timestamp: When the request was made (UTC).
        endpoint: The requested endpoint path.
        method: HTTP method (e.g., GET, POST).
        status_code: HTTP status code of the response.
        response_time: Time taken to process the request (seconds).
        user_ip: Client's IP address.
        user_agent: Client's user agent string.
    """
    __tablename__ = 'analytics'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    endpoint = Column(String)
    method = Column(String)
    status_code = Column(Integer)
    response_time = Column(Float)
    user_ip = Column(String)
    user_agent = Column(String)


class FlaskRealTimeAnalytics:
    """Flask extension for real-time analytics dashboards.

    Tracks user behavior, API usage, and performance metrics, with WebSocket
    updates for live dashboards. Integrates with SQLAlchemy databases.

    Args:
        app: Flask application instance (optional, for deferred initialization).
        db: SQLAlchemy database instance (optional, for deferred initialization).

    Attributes:
        app: Flask application instance.
        db: SQLAlchemy database instance.
        socketio: Flask-SocketIO instance for WebSocket communication.
        Session: SQLAlchemy session factory for database operations.
    """
    def __init__(self, app=None, db=None):
        self.app = app
        self.db = db
        self.socketio = None
        self.Session = None
        if app is not None and db is not None:
            self.init_app(app, db)

    def init_app(self, app: Flask, db):
        """Initialize the extension with a Flask app and SQLAlchemy database.

        Args:
            app: Flask application instance.
            db: SQLAlchemy database instance.

        Raises:
            ValueError: If app or db is None.
        """
        if app is None or db is None:
            raise ValueError("Both app and db must be provided.")
        self.db = db
        self.socketio = SocketIO(app)
        Base.metadata.create_all(self.db.engine)
        self.Session = sessionmaker(bind=self.db.engine)
        self.register_middleware(app)
        self.register_routes(app)
        self.register_socketio_events()

    def track(self, f):
        """Decorator to track request analytics for a view function.

        Measures response time and logs request details (endpoint, method, status,
        etc.) to the database. Emits WebSocket updates with summary stats.

        Args:
            f: View function to decorate.

        Returns:
            Callable: Decorated function that tracks analytics and returns a response.
        """
        @wraps(f)
        def decorated(*args, **kwargs):
            start_time = time.time()
            result = f(*args, **kwargs)
            response = make_response(result)
            response_time = time.time() - start_time
            self.log_request(
                endpoint=request.path,
                method=request.method,
                status_code=response.status_code,
                response_time=response_time,
                user_ip=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            return response
        return decorated

    def register_middleware(self, app: Flask):
        """Register middleware to apply tracking to all view functions.

        Automatically wraps view functions with the track decorator unless already
        tracked.

        Args:
            app: Flask application instance.
        """
        @app.before_request
        def apply_tracking():
            if request.endpoint:
                view_func = app.view_functions[request.endpoint]
                if not hasattr(view_func, '_tracked'):
                    app.view_functions[request.endpoint] = self.track(view_func)
                    view_func._tracked = True

    def log_request(self, endpoint, method, status_code, response_time, user_ip, user_agent):
        """Log a request's analytics data to the database.

        Args:
            endpoint: Requested endpoint path.
            method: HTTP method (e.g., GET, POST).
            status_code: HTTP status code of the response.
            response_time: Time taken to process the request (seconds).
            user_ip: Client's IP address.
            user_agent: Client's user agent string.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: If database operations fail.
        """
        session = self.Session()
        record = AnalyticsRecord(
            timestamp=datetime.now(UTC),
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            response_time=response_time,
            user_ip=user_ip,
            user_agent=user_agent
        )
        session.add(record)
        session.commit()
        self.socketio.emit('analytics_update', self.get_summary_stats())
        session.close()

    def get_summary_stats(self):
        """Retrieve summary statistics from the analytics database.

        Returns:
            dict: Statistics including total requests, endpoint counts, and average
                response time.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: If database queries fail.
        """
        session = self.Session()
        total_requests = session.query(AnalyticsRecord).count()
        endpoint_counts = dict(
            session.query(AnalyticsRecord.endpoint, func.count(AnalyticsRecord.endpoint))
            .group_by(AnalyticsRecord.endpoint).all()
        )
        avg_response_time = session.query(func.avg(AnalyticsRecord.response_time)).scalar() or 0
        session.close()
        return {
            'total_requests': total_requests,
            'endpoint_counts': endpoint_counts,
            'avg_response_time': round(avg_response_time, 3)
        }

    def register_routes(self, app: Flask):
        """Register analytics dashboard route.

        Adds the /analytics route to display the real-time dashboard.

        Args:
            app: Flask application instance.
        """
        @app.route('/analytics')
        def analytics_dashboard():
            """Render the analytics dashboard.

            Returns:
                str: Rendered HTML template for the dashboard.
            """
            return render_template('analytics.html', stats=self.get_summary_stats())

    def register_socketio_events(self):
        """Register WebSocket event handlers for real-time updates.

        Emits initial analytics data on client connection.
        """
        @self.socketio.on('connect')
        def handle_connect():
            """Handle WebSocket client connection.

            Sends current analytics summary to the connected client.
            """
            self.socketio.emit('analytics_update', self.get_summary_stats())
