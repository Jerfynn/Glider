"""
Hardware-accelerated 3D OpenGL Viewport for Underwater Glider Orientation.
Hyper-realistic Oceanic Water Environment with Animated Sunlight Rays (God Rays),
Depth Gradient, Surface Waves, Marine Dust Particles, and Corner Orientation Gizmo.
"""

import math
import random
import time
import numpy as np

# Disable strict PyOpenGL error checking for performance & driver compatibility
try:
    import OpenGL
    OpenGL.ERROR_CHECKING = False
except Exception:
    pass

# Cross-platform Qt OpenGL Widget import
try:
    from qtpy.QtOpenGLWidgets import QOpenGLWidget
except (ImportError, Exception):
    from qtpy.QtWidgets import QOpenGLWidget

from qtpy.QtCore import Qt, QTimer
from qtpy.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame
)
from qtpy.QtGui import QColor, QPainter, QFont, QPen

# OpenGL imports
from OpenGL.GL import *
from OpenGL.GLU import *

from app.config import COLORS
from app.utils.icons import get_icon


class Glider3DCanvas(QOpenGLWidget):
    """
    OpenGL 3D Scene rendering the underwater glider inside a realistic
    dynamic oceanic water environment with sunbeams, depth gradient,
    subtle surface water waves, floating marine particles, and corner 3-axis gizmo.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Glider Orientation Angles (Degrees) - Default to zero
        self.roll: float = 0.0
        self.pitch: float = 0.0
        self.yaw: float = 0.0
        
        # Target angles for smooth interpolation
        self.target_roll: float = 0.0
        self.target_pitch: float = 0.0
        self.target_yaw: float = 0.0

        # Camera controls
        self.camera_dist = 5.5
        self.camera_pitch = 18.0
        self.camera_yaw = -45.0
        self.pan_x = 0.0
        self.pan_y = 0.0

        # Mouse interaction state
        self.last_mouse_pos = None
        self.mouse_mode = "ORBIT"

        # Animation clock
        self.anim_time = 0.0

        # Generate persistent 3D marine dust / plankton particles
        np.random.seed(42)
        num_particles = 120
        self.particle_positions = np.random.uniform(-4.5, 4.5, size=(num_particles, 3))
        self.particle_speeds = np.random.uniform(0.15, 0.45, size=num_particles)
        self.particle_sizes = np.random.uniform(1.2, 2.5, size=num_particles)
        self.particle_phases = np.random.uniform(0, math.pi * 2, size=num_particles)

        # Smooth animation timer (~60 FPS)
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self._animate_step)
        self.anim_timer.start(16)

    def set_orientation(self, roll: float, pitch: float, yaw: float):
        """Update orientation from telemetry."""
        self.target_roll = roll
        self.target_pitch = pitch
        self.target_yaw = yaw

    def reset_camera(self):
        """Snaps camera back to default isometric viewing angle."""
        self.camera_dist = 5.5
        self.camera_pitch = 18.0
        self.camera_yaw = -45.0
        self.pan_x = 0.0
        self.pan_y = 0.0
        self.update()

    def _animate_step(self):
        """Smoothly interpolates orientation and advances water physics time."""
        lerp_factor = 0.25
        yaw_diff = (self.target_yaw - self.yaw + 180.0) % 360.0 - 180.0
        
        self.roll += (self.target_roll - self.roll) * lerp_factor
        self.pitch += (self.target_pitch - self.pitch) * lerp_factor
        self.yaw = (self.yaw + yaw_diff * lerp_factor) % 360.0

        self.anim_time += 0.016
        self.update()

    # --- OpenGL Pipeline ---

    def initializeGL(self):
        """Sets up realistic underwater lighting, fog, and blending."""
        try:
            glClearColor(0.03, 0.15, 0.28, 1.0)
            glEnable(GL_DEPTH_TEST)
            glDepthFunc(GL_LEQUAL)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            
            glShadeModel(GL_SMOOTH)
            glEnable(GL_NORMALIZE)

            # Underwater Ocean Depth Fog
            glEnable(GL_FOG)
            glFogi(GL_FOG_MODE, GL_EXP2)
            glFogfv(GL_FOG_COLOR, [0.035, 0.16, 0.28, 1.0])
            glFogf(GL_FOG_DENSITY, 0.052)
            glHint(GL_FOG_HINT, GL_NICEST)

            # Realistic Sunlight & Aquatic Ambient Lighting setup
            glEnable(GL_LIGHTING)
            glEnable(GL_LIGHT0)
            
            light_pos = [3.0, 8.0, 5.0, 1.0]
            glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
            glLightfv(GL_LIGHT0, GL_AMBIENT, [0.22, 0.38, 0.52, 1.0])
            glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.88, 0.94, 0.98, 1.0])
            glLightfv(GL_LIGHT0, GL_SPECULAR, [0.75, 0.90, 0.98, 1.0])

            glEnable(GL_LIGHT1)
            glLightfv(GL_LIGHT1, GL_POSITION, [-4.0, -6.0, -3.0, 1.0])
            glLightfv(GL_LIGHT1, GL_DIFFUSE, [0.06, 0.18, 0.30, 1.0])

            glEnable(GL_COLOR_MATERIAL)
            glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
            glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [0.45, 0.50, 0.55, 1.0])
            glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 36.0)
        except Exception:
            pass

    def resizeGL(self, w: int, h: int):
        """Handles viewport resizing and projection matrix update."""
        if h == 0:
            h = 1
        try:
            glViewport(0, 0, w, h)
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            gluPerspective(45.0, float(w) / float(h), 0.1, 100.0)
            glMatrixMode(GL_MODELVIEW)
        except Exception:
            pass

    def paintGL(self):
        """Draws the entire 3D realistic ocean scene."""
        try:
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            w = self.width()
            h = self.height() if self.height() > 0 else 1

            # 1. Render Realistic Oceanic Vertical Depth Gradient Backdrop (2D Ortho Pass)
            self._draw_ocean_depth_gradient(w, h)

            # Restore 3D Perspective Projection
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            gluPerspective(45.0, float(w) / float(h), 0.1, 100.0)
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()

            # Camera positioning
            glTranslated(self.pan_x, self.pan_y, -self.camera_dist)
            glRotatef(self.camera_pitch, 1.0, 0.0, 0.0)
            glRotatef(self.camera_yaw, 0.0, 1.0, 0.0)

            # 2. Render Volumetric Sunlight Shafts (God Rays)
            self._draw_sunlight_shafts()

            # 3. Render Overhead Translucent Water Surface Waves
            self._draw_water_surface_waves()

            # 4. Render Suspended Marine Dust / Plankton Particles
            self._draw_marine_particles()

            # 5. Render 3D Underwater Glider Model with Euler Rotations
            glPushMatrix()
            glRotatef(-self.yaw, 0.0, 1.0, 0.0)    # Yaw
            glRotatef(self.pitch, 1.0, 0.0, 0.0)   # Pitch
            glRotatef(self.roll, 0.0, 0.0, 1.0)    # Roll

            self._draw_glider_model()
            glPopMatrix()

            # 6. Render Dynamic Corner 3-Axis Orientation Indicator (Side Overlay)
            self._draw_dynamic_corner_gizmo()
        except Exception:
            pass

    def _draw_ocean_depth_gradient(self, w: int, h: int):
        """Draws a smooth vertical ocean depth backdrop from sunlit surface turquoise to abyssal navy."""
        glPushAttrib(GL_ALL_ATTRIB_BITS)
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_FOG)

        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, w, 0, h, -1, 1)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        glBegin(GL_QUADS)
        # Top: Sunlit turquoise / aqua ocean surface
        glColor3f(0.08, 0.38, 0.58)
        glVertex2f(0, h)
        glVertex2f(w, h)

        # Bottom: Deep abyssal navy
        glColor3f(0.015, 0.07, 0.16)
        glVertex2f(w, 0)
        glVertex2f(0, 0)
        glEnd()

        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopAttrib()

    def _draw_sunlight_shafts(self):
        """Draws animated translucent volumetric sunbeams (God Rays) shining down through water."""
        glPushAttrib(GL_ALL_ATTRIB_BITS)
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        glDepthMask(GL_FALSE)

        t = self.anim_time

        rays = [
            (-2.2, 0.35, 1.2),
            (-0.8, -0.2, 0.9),
            (0.7, 0.4, 1.1),
            (2.0, -0.3, 0.8),
            (-1.5, 1.2, 0.7),
            (1.2, -1.0, 1.0),
        ]

        top_y = 3.6
        bottom_y = -3.8

        glBegin(GL_TRIANGLES)
        for idx, (x_pos, z_pos, width) in enumerate(rays):
            shimmer = 0.08 + 0.04 * math.sin(t * 1.6 + idx * 1.5)
            sway = math.sin(t * 0.8 + idx) * 0.25

            # Top apex
            glColor4f(0.45, 0.85, 0.98, shimmer * 1.6)
            glVertex3f(x_pos + sway, top_y, z_pos)

            # Bottom left beam edge
            glColor4f(0.10, 0.45, 0.70, 0.0)
            glVertex3f(x_pos - width * 1.5 + sway * 1.8, bottom_y, z_pos - 0.8)

            # Bottom right beam edge
            glColor4f(0.10, 0.45, 0.70, 0.0)
            glVertex3f(x_pos + width * 1.5 + sway * 1.8, bottom_y, z_pos + 0.8)

        glEnd()

        glDepthMask(GL_TRUE)
        glPopAttrib()

    def _draw_water_surface_waves(self):
        """Draws a translucent undulating water surface above the glider with moving ripples."""
        glPushAttrib(GL_ALL_ATTRIB_BITS)
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDepthMask(GL_FALSE)

        t = self.anim_time
        y_base = 3.4
        grid_size = 6.0
        steps = 14
        step_sz = (grid_size * 2) / steps

        glBegin(GL_QUADS)
        for i in range(steps):
            x1 = -grid_size + i * step_sz
            x2 = x1 + step_sz
            for j in range(steps):
                z1 = -grid_size + j * step_sz
                z2 = z1 + step_sz

                h1 = math.sin(x1 * 0.8 + t * 1.8) * math.cos(z1 * 0.8 + t * 1.4) * 0.09
                h2 = math.sin(x2 * 0.8 + t * 1.8) * math.cos(z1 * 0.8 + t * 1.4) * 0.09
                h3 = math.sin(x2 * 0.8 + t * 1.8) * math.cos(z2 * 0.8 + t * 1.4) * 0.09
                h4 = math.sin(x1 * 0.8 + t * 1.8) * math.cos(z2 * 0.8 + t * 1.4) * 0.09

                alpha = 0.14 + (h1 + 0.09) * 0.4

                glColor4f(0.50, 0.88, 0.98, max(0.04, min(0.35, alpha)))
                glVertex3f(x1, y_base + h1, z1)
                glVertex3f(x2, y_base + h2, z1)
                glVertex3f(x2, y_base + h3, z2)
                glVertex3f(x1, y_base + h4, z2)

        glEnd()
        glDepthMask(GL_TRUE)
        glPopAttrib()

    def _draw_marine_particles(self):
        """Draws drifting marine snow particles / micro-bubbles in 3D open water."""
        glPushAttrib(GL_ALL_ATTRIB_BITS)
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        glDepthMask(GL_FALSE)

        t = self.anim_time

        glBegin(GL_POINTS)
        for i in range(len(self.particle_positions)):
            px, py, pz = self.particle_positions[i]
            phase = self.particle_phases[i]
            speed = self.particle_speeds[i]
            
            drift_x = px + math.sin(t * speed + phase) * 0.35
            drift_y = py + math.cos(t * speed * 0.7 + phase) * 0.25
            drift_z = pz + math.sin(t * speed * 0.5 + phase) * 0.35

            glow = 0.25 + 0.20 * math.sin(t * 2.0 + phase)
            glColor4f(0.65, 0.90, 1.0, glow)
            glPointSize(self.particle_sizes[i])
            glVertex3f(drift_x, drift_y, drift_z)

        glEnd()

        glDepthMask(GL_TRUE)
        glPopAttrib()

    def _draw_dynamic_corner_gizmo(self):
        """
        Draws the 3-axis orientation gizmo placed on the bottom-left side of the viewport.
        Dynamically rotates with respect to the 3 vehicle axes (Roll, Pitch, Yaw) and camera view.
        """
        glPushAttrib(GL_ALL_ATTRIB_BITS)
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_FOG)

        gizmo_size = 90
        glViewport(18, 42, gizmo_size, gizmo_size)

        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(-1.4, 1.4, -1.4, 1.4, -5.0, 5.0)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        # Apply Camera view rotation followed by vehicle orientation (Roll, Pitch, Yaw)
        glRotatef(self.camera_pitch, 1.0, 0.0, 0.0)
        glRotatef(self.camera_yaw, 0.0, 1.0, 0.0)
        glRotatef(-self.yaw, 0.0, 1.0, 0.0)
        glRotatef(self.pitch, 1.0, 0.0, 0.0)
        glRotatef(self.roll, 0.0, 0.0, 1.0)

        glLineWidth(2.5)

        # Draw 3-Axis Lines
        glBegin(GL_LINES)
        # X Axis - Coral Red (Forward-Aft)
        glColor3f(0.95, 0.25, 0.25)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.85, 0.0, 0.0)

        # Y Axis - Emerald Green (Starboard-Port)
        glColor3f(0.20, 0.85, 0.40)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, 0.85, 0.0)

        # Z Axis - Cyan Blue (Vertical)
        glColor3f(0.30, 0.75, 1.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, 0.0, 0.85)
        glEnd()

        # Endpoint tips
        quad = gluNewQuadric()
        
        # X tip (Coral Red)
        glColor3f(0.95, 0.25, 0.25)
        glPushMatrix()
        glTranslatef(0.85, 0.0, 0.0)
        gluSphere(quad, 0.07, 12, 8)
        glPopMatrix()

        # Y tip (Emerald Green)
        glColor3f(0.20, 0.85, 0.40)
        glPushMatrix()
        glTranslatef(0.0, 0.85, 0.0)
        gluSphere(quad, 0.07, 12, 8)
        glPopMatrix()

        # Z tip (Cyan Blue)
        glColor3f(0.30, 0.75, 1.0)
        glPushMatrix()
        glTranslatef(0.0, 0.0, 0.85)
        gluSphere(quad, 0.07, 12, 8)
        glPopMatrix()

        # Center Origin dot
        glColor3f(0.85, 0.90, 0.95)
        gluSphere(quad, 0.06, 12, 8)
        gluDeleteQuadric(quad)

        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

        w = self.width()
        h = self.height() if self.height() > 0 else 1
        glViewport(0, 0, w, h)
        glPopAttrib()

    def _draw_glider_model(self):
        """Draws industrial-finish Underwater Glider with realistic aquatic specular sheen."""
        # Bright Industrial Marine Yellow Hull
        glColor3f(0.95, 0.72, 0.12)
        
        quad = gluNewQuadric()
        gluQuadricNormals(quad, GLU_SMOOTH)
        
        # Center cylindrical body
        glPushMatrix()
        glTranslatef(0.0, 0.0, -1.0)
        gluCylinder(quad, 0.32, 0.32, 2.0, 32, 16)
        glPopMatrix()

        # Nose transition
        glPushMatrix()
        glTranslatef(0.0, 0.0, 1.0)
        gluCylinder(quad, 0.32, 0.22, 0.4, 32, 8)
        glPopMatrix()

        # Dark Marine Nose Dome
        glColor3f(0.08, 0.12, 0.18)
        glPushMatrix()
        glTranslatef(0.0, 0.0, 1.4)
        gluSphere(quad, 0.22, 32, 16)
        glPopMatrix()

        # Dark Collar Bands
        glColor3f(0.08, 0.12, 0.18)
        glPushMatrix()
        glTranslatef(0.0, 0.0, 0.55)
        gluCylinder(quad, 0.33, 0.33, 0.08, 32, 4)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(0.0, 0.0, -0.45)
        gluCylinder(quad, 0.33, 0.33, 0.10, 32, 4)
        glPopMatrix()

        # Tapered Tail Section
        glColor3f(0.95, 0.72, 0.12)
        glPushMatrix()
        glTranslatef(0.0, 0.0, -1.0)
        glRotatef(180, 1.0, 0.0, 0.0)
        gluCylinder(quad, 0.32, 0.14, 0.8, 32, 16)
        glPopMatrix()

        # Swept Glider Wings
        self._draw_wing_pair()

        # Tail Fin / Stabilizers
        self._draw_tail_fins()

        # Rear Propulsion Hub
        glColor3f(0.12, 0.18, 0.25)
        glPushMatrix()
        glTranslatef(0.0, 0.0, -1.85)
        gluCylinder(quad, 0.18, 0.18, 0.25, 24, 4)
        gluSphere(quad, 0.10, 16, 8)
        glPopMatrix()

        # Propeller Blades
        glColor3f(0.95, 0.72, 0.12)
        for i in range(3):
            glPushMatrix()
            glTranslatef(0.0, 0.0, -1.82)
            glRotatef(i * 120 + (self.yaw * 5), 0.0, 0.0, 1.0)
            glBegin(GL_TRIANGLES)
            glNormal3f(0.0, 0.0, 1.0)
            glVertex3f(-0.03, 0.0, 0.0)
            glVertex3f(0.03, 0.0, 0.0)
            glVertex3f(0.0, 0.16, 0.03)
            glEnd()
            glPopMatrix()

        # Antenna Mast
        glColor3f(0.08, 0.12, 0.18)
        glPushMatrix()
        glTranslatef(0.0, 0.32, 0.1)
        gluCylinder(quad, 0.04, 0.03, 0.35, 12, 4)
        glTranslatef(0.0, 0.0, 0.35)
        gluSphere(quad, 0.045, 12, 8)
        glPopMatrix()

        gluDeleteQuadric(quad)

    def _draw_wing_pair(self):
        wing_span = 1.8
        root_chord = 0.55
        tip_chord = 0.25
        sweep = 0.35
        thickness = 0.04

        glBegin(GL_QUADS)
        # Right Wing Upper Face
        glNormal3f(0.0, 1.0, 0.0)
        glVertex3f(0.28, thickness, 0.2)
        glVertex3f(wing_span, thickness, 0.2 - sweep)
        glVertex3f(wing_span, thickness, 0.2 - sweep - tip_chord)
        glVertex3f(0.28, thickness, 0.2 - root_chord)

        # Right Wing Lower Face
        glNormal3f(0.0, -1.0, 0.0)
        glVertex3f(0.28, -thickness, 0.2 - root_chord)
        glVertex3f(wing_span, -thickness, 0.2 - sweep - tip_chord)
        glVertex3f(wing_span, -thickness, 0.2 - sweep)
        glVertex3f(0.28, -thickness, 0.2)

        # Left Wing Upper Face
        glNormal3f(0.0, 1.0, 0.0)
        glVertex3f(-0.28, thickness, 0.2)
        glVertex3f(-0.28, thickness, 0.2 - root_chord)
        glVertex3f(-wing_span, thickness, 0.2 - sweep - tip_chord)
        glVertex3f(-wing_span, thickness, 0.2 - sweep)

        # Left Wing Lower Face
        glNormal3f(0.0, -1.0, 0.0)
        glVertex3f(-0.28, -thickness, 0.2)
        glVertex3f(-wing_span, -thickness, 0.2 - sweep)
        glVertex3f(-wing_span, -thickness, 0.2 - sweep - tip_chord)
        glVertex3f(-0.28, -thickness, 0.2 - root_chord)
        glEnd()

        # Wing leading and trailing edge caps
        glBegin(GL_QUADS)
        glNormal3f(0.3, 0.0, 1.0)
        glVertex3f(0.28, thickness, 0.2)
        glVertex3f(0.28, -thickness, 0.2)
        glVertex3f(wing_span, -thickness, 0.2 - sweep)
        glVertex3f(wing_span, thickness, 0.2 - sweep)

        glNormal3f(-0.3, 0.0, 1.0)
        glVertex3f(-0.28, thickness, 0.2)
        glVertex3f(-wing_span, thickness, 0.2 - sweep)
        glVertex3f(-wing_span, -thickness, 0.2 - sweep)
        glVertex3f(-0.28, -thickness, 0.2)
        glEnd()

    def _draw_tail_fins(self):
        glColor3f(0.95, 0.72, 0.12)
        
        glBegin(GL_TRIANGLES)
        glNormal3f(1.0, 0.0, 0.0)
        glVertex3f(0.02, 0.15, -1.1)
        glVertex3f(0.02, 0.65, -1.65)
        glVertex3f(0.02, 0.15, -1.75)

        glNormal3f(-1.0, 0.0, 0.0)
        glVertex3f(-0.02, 0.15, -1.75)
        glVertex3f(-0.02, 0.65, -1.65)
        glVertex3f(-0.02, 0.15, -1.1)
        glEnd()

    # --- Mouse Interaction ---

    def mousePressEvent(self, event):
        self.last_mouse_pos = event.position() if hasattr(event, "position") else event.pos()
        if event.button() == Qt.RightButton:
            self.mouse_mode = "PAN"
        else:
            self.mouse_mode = "ORBIT"

    def mouseMoveEvent(self, event):
        if self.last_mouse_pos is None:
            return
        
        curr_pos = event.position() if hasattr(event, "position") else event.pos()
        dx = curr_pos.x() - self.last_mouse_pos.x()
        dy = curr_pos.y() - self.last_mouse_pos.y()

        if self.mouse_mode == "ORBIT":
            self.camera_yaw += dx * 0.45
            self.camera_pitch += dy * 0.45
            self.camera_pitch = max(-89.0, min(89.0, self.camera_pitch))
        elif self.mouse_mode == "PAN":
            self.pan_x += dx * 0.005 * (self.camera_dist / 5.0)
            self.pan_y -= dy * 0.005 * (self.camera_dist / 5.0)

        self.last_mouse_pos = curr_pos
        self.update()

    def mouseReleaseEvent(self, event):
        self.last_mouse_pos = None

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        zoom_factor = 0.9 if delta > 0 else 1.1
        self.camera_dist = max(1.5, min(25.0, self.camera_dist * zoom_factor))
        self.update()


class Glider3DViewWidget(QFrame):
    """
    Container widget wrapping the 3D OpenGL Canvas with an overlaid floating
    GCS navigation toolbar.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 6)
        layout.setSpacing(4)

        # 3D Canvas
        self.canvas = Glider3DCanvas(self)
        layout.addWidget(self.canvas, 1)

        # Bottom Floating Action Controls:
        # [Reset View] [Pan] [Rotate] [Zoom In] [Zoom Out] [Fit View]
        bottom_bar = QHBoxLayout()
        bottom_bar.setContentsMargins(8, 0, 8, 0)
        bottom_bar.setSpacing(6)
        bottom_bar.addStretch()

        self.btn_reset = QPushButton(" Reset View")
        self.btn_reset.setObjectName("NavToolButton")
        self.btn_reset.setIcon(get_icon("reset_view", color=COLORS["text_secondary"], size=12))
        self.btn_reset.clicked.connect(self.canvas.reset_camera)

        self.btn_pan = QPushButton(" Pan")
        self.btn_pan.setObjectName("NavToolButton")
        self.btn_pan.setIcon(get_icon("pan", color=COLORS["text_secondary"], size=12))
        self.btn_pan.clicked.connect(lambda: setattr(self.canvas, "mouse_mode", "PAN"))

        self.btn_rotate = QPushButton(" Rotate")
        self.btn_rotate.setObjectName("NavToolButton")
        self.btn_rotate.setIcon(get_icon("rotate", color=COLORS["text_secondary"], size=12))
        self.btn_rotate.clicked.connect(lambda: setattr(self.canvas, "mouse_mode", "ORBIT"))

        self.btn_zoom_in = QPushButton(" Zoom In")
        self.btn_zoom_in.setObjectName("NavToolButton")
        self.btn_zoom_in.setIcon(get_icon("zoom_in", color=COLORS["text_secondary"], size=12))
        self.btn_zoom_in.clicked.connect(self._zoom_in)

        self.btn_zoom_out = QPushButton(" Zoom Out")
        self.btn_zoom_out.setObjectName("NavToolButton")
        self.btn_zoom_out.setIcon(get_icon("zoom_out", color=COLORS["text_secondary"], size=12))
        self.btn_zoom_out.clicked.connect(self._zoom_out)

        self.btn_fit = QPushButton(" Fit View")
        self.btn_fit.setObjectName("NavToolButton")
        self.btn_fit.setIcon(get_icon("fit_view", color=COLORS["text_secondary"], size=12))
        self.btn_fit.clicked.connect(self.canvas.reset_camera)

        bottom_bar.addWidget(self.btn_reset)
        bottom_bar.addWidget(self.btn_pan)
        bottom_bar.addWidget(self.btn_rotate)
        bottom_bar.addWidget(self.btn_zoom_in)
        bottom_bar.addWidget(self.btn_zoom_out)
        bottom_bar.addWidget(self.btn_fit)
        bottom_bar.addStretch()

        layout.addLayout(bottom_bar)

    def _zoom_in(self):
        self.canvas.camera_dist = max(1.5, self.canvas.camera_dist * 0.85)
        self.canvas.update()

    def _zoom_out(self):
        self.canvas.camera_dist = min(25.0, self.canvas.camera_dist * 1.15)
        self.canvas.update()

    def update_telemetry(self, roll: float, pitch: float, yaw: float):
        """Pass orientation updates into the 3D canvas."""
        self.canvas.set_orientation(roll, pitch, yaw)
