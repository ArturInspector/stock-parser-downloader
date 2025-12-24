from PyQt6.QtWidgets import (QGraphicsView, QGraphicsScene, QGraphicsProxyWidget, 
                            QFrame, QVBoxLayout, QLabel, QGraphicsRotation, QWidget)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty, QUrl
from PyQt6.QtGui import QVector3D, QPainter, QPixmap
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest

class TiltCard(QGraphicsView):
    def __init__(self, title, subtitle, preview_url=None, parent=None):
        super().__init__(parent)
        self.setFixedSize(310, 260) 
        self.setStyleSheet("background: transparent; border: none;")
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setFrameShape(QFrame.Shape.NoFrame)
        
        # Scene setup
        self.scene = QGraphicsScene(0, 0, 310, 260, self)
        self.setScene(self.scene)
        
        # Content widget
        self.content = QFrame()
        self.content.setFixedSize(270, 220)
        self.content.setObjectName("Card")
        self.content.setStyleSheet("""
            QFrame#Card {
                background-color: #18181b;
                border: 1px solid #27272a;
                border-radius: 12px;
            }
        """)
        
        layout = QVBoxLayout(self.content)
        layout.setContentsMargins(0, 0, 0, 16)
        layout.setSpacing(12)
        
        # Image Preview
        self.image_label = QLabel()
        self.image_label.setFixedSize(270, 140)
        self.image_label.setStyleSheet("""
            background-color: #09090b;
            border-top-left-radius: 11px;
            border-top-right-radius: 11px;
            border-bottom: 1px solid #27272a;
        """)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setText("Loading...")
        
        # Text container (for margins)
        text_container = QWidget()
        text_layout = QVBoxLayout(text_container)
        text_layout.setContentsMargins(16, 0, 16, 0)
        text_layout.setSpacing(4)
        
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #ffffff;")
        self.title_label.setWordWrap(True)
        
        self.subtitle_label = QLabel(subtitle)
        self.subtitle_label.setStyleSheet("font-size: 11px; color: #22d3ee;")
        
        text_layout.addWidget(self.title_label)
        text_layout.addWidget(self.subtitle_label)
        
        layout.addWidget(self.image_label)
        layout.addWidget(text_container)
        
        # Network manager for image
        self.manager = QNetworkAccessManager(self)
        self.manager.finished.connect(self.on_image_loaded)
        if preview_url:
            self.manager.get(QNetworkRequest(QUrl(preview_url)))
        else:
            self.image_label.setText("No Preview")

        # Proxy for 3D setup (moved from on_image_loaded)
        self.proxy = self.scene.addWidget(self.content)
        self.proxy.setPos(20, 20)
        
        self.x_rotation = QGraphicsRotation(self.proxy)
        self.x_rotation.setAxis(Qt.Axis.YAxis)
        self.x_rotation.setOrigin(QVector3D(135, 110, 0))
        
        self.y_rotation = QGraphicsRotation(self.proxy)
        self.y_rotation.setAxis(Qt.Axis.XAxis)
        self.y_rotation.setOrigin(QVector3D(135, 110, 0))
        
        self.proxy.setTransformations([self.x_rotation, self.y_rotation])
        
        self.anim_x = QPropertyAnimation(self.x_rotation, b"angle")
        self.anim_y = QPropertyAnimation(self.y_rotation, b"angle")
        for anim in [self.anim_x, self.anim_y]:
            anim.setDuration(300)
            anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def on_image_loaded(self, reply):
        if reply.error() == reply.NetworkError.NoError:
            data = reply.readAll()
            pixmap = QPixmap()
            pixmap.loadFromData(data)
            if not pixmap.isNull():
                scaled = pixmap.scaled(270, 140, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
                self.image_label.setPixmap(scaled)
                self.image_label.setText("")
            else:
                self.image_label.setText("Error")
        else:
            self.image_label.setText("Error")
        reply.deleteLater()

    def mouseMoveEvent(self, event):
        # Center of 310x260 view is (155, 130)
        rel_x = event.position().x() - 155
        rel_y = event.position().y() - 130
        
        max_tilt = 10 
        tilt_x = (rel_x / 155) * max_tilt
        tilt_y = -(rel_y / 130) * max_tilt
        
        self.x_rotation.setAngle(tilt_x)
        self.y_rotation.setAngle(tilt_y)
        
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        self.anim_x.setEndValue(0)
        self.anim_y.setEndValue(0)
        self.anim_x.start()
        self.anim_y.start()
        super().leaveEvent(event)

    def enterEvent(self, event):
        self.anim_x.stop()
        self.anim_y.stop()
        super().enterEvent(event)
