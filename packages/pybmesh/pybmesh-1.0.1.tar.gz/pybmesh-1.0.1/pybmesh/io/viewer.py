#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 27/01/2025
Last modified on 14/02/2025

Author: Alexis Sauvageon
Email: alexis.sauvageon@gmail.com

Description: This module provides the functionality to display mesh objects using VTK and PyQt.
It includes the `plot` function that creates a `Viewer` window to display one or more mesh objects. 
The `Viewer` class, a subclass of `QMainWindow`, integrates VTK for 3D rendering with a Qt-based GUI, 
allowing users to interact with meshes through camera controls, visibility toggles, and annotations.

The module provides the following features:
- Interactive 3D mesh visualization using VTK.
- Camera control (top, bottom, front, back, isometric, etc.).
- Mesh representation options (points, surface, surface with edges, wireframe).
- Support for annotations like node/element IDs, mesh labels, and orientation (normals).
- Customizable interface with checkboxes for mesh visibility and toolbar for camera and opacity controls.
"""

import vtk
import os,sys
import re
import inspect
import random
import numpy as np
from pybmesh.geom.mesh import MeshComponent,MeshAssembly
from pybmesh.utils.constants import _ICON_DICT, _MAX_ITEM_DISPLAYED
from pybmesh.io.vtk2numpy import  vtk_to_numpy_connectivity, numpy_to_vtk_connectivity
from pybmesh.utils.miscutils import strip_brackets
from PySide6  import QtWidgets, QtCore, QtGui
from vtkmodules.vtkFiltersExtraction import vtkExtractGeometry
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

def plot(*objs):
    """
    Create a Viewer, plot each Mesh object passed as an argument, and show the viewer.

    Args:
        *objs: One or more Mesh objects to display.

    Example:
        >>> display(mesh1, mesh2)
    """
    if len(objs) == 1 and not isinstance(objs[0], (str, bytes)) and hasattr(objs[0], '__iter__'):
        objs = list(objs[0])  # Unpack the list/tuple

    try:
        frame = inspect.currentframe().f_back
        caller_line = inspect.getframeinfo(frame).code_context[0].strip()

        start = caller_line.find("plot(")
        end = caller_line.rfind(")")  # Ensure correct closing parenthesis

        if start != -1 and end != -1:
            arg_str = caller_line[start + len("plot("):end].strip()

            # If the argument string is enclosed in brackets/parentheses, remove them.
            arg_str = strip_brackets(arg_str)

            # Handle single argument cases correctly.
            if len(objs) == 1 and "," not in arg_str:
                labels = [arg_str]
            else:
                # Split arguments carefully, preserving structures inside brackets.
                labels = [s.strip() for s in re.split(r',(?![^{]*\})', arg_str)]
            # If labels extraction fails, provide default labels.
            if len(labels) != len(objs):
                labels = [f"Object {i}" for i in range(len(objs))]
        else:
            labels = [f"Object {i}" for i in range(len(objs))]
    except Exception as e:
        print(f"Exception: {e}")  # Debugging line
        labels = [f"Object {i}" for i in range(len(objs))]

    objs, labels = zip(*sorted(zip(objs, labels), key=lambda x: x[1]))
    # Create new lists for objects and labels.
    new_objs = []
    new_labels = []
    for obj, label in zip(objs, labels):
        # Check if the object is a MeshComponent (assumes MeshComponent is defined)
        if isinstance(obj, MeshComponent) or isinstance(obj,MeshAssembly):
            # For MeshComponent, add each object from its internal dictionary.
            for key, child in obj.internal.items():
                new_objs.append(child)
                new_labels.append(key)
            # Also add each object from its boundary dictionary.
            for key, child in obj.boundary.items():
                new_objs.append(child)
                new_labels.append(key)
        else:
            new_objs.append(obj)
            new_labels.append(label)
    
    # Optionally, sort the expanded list as well.
    objs, labels = zip(*sorted(zip(new_objs, new_labels), key=lambda x: x[1]))

    # Use the existing QApplication if present.
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)

    Viewer(list(objs), list(labels))
    app.exec_()


# =============================================================================
# Viewer class: a QMainWindow that displays the VTK render window and
# a left panel with checkboxes for each mesh.
# =============================================================================
class Viewer(QtWidgets.QMainWindow):
    def __init__(self, mesh_objs, labels, parent=None):
        """
        Initialize the Viewer with mesh objects and their corresponding labels.

        Parameters:
          mesh_objs - list of mesh objects. Each mesh must implement
                      get_vtk_unstructured_grid() and have a .color attribute.
          labels    - list of strings used to label each object (in the left panel)
        """
        super(Viewer, self).__init__(parent)
        self.setWindowTitle("VTK Viewer")
        self.resize(720,480)
        self.mesh_items = []  # Will store tuples of (label, mesh, actor)

        # Create central widget for VTK.
        central_frame = QtWidgets.QFrame()
        central_layout = QtWidgets.QVBoxLayout(central_frame)
        self.vtkWidget = QVTKRenderWindowInteractor(central_frame)
        central_layout.addWidget(self.vtkWidget)
        self.setCentralWidget(central_frame)

        # Set up the VTK renderer and interactor.
        self.renderer = vtk.vtkRenderer()
        self.renderer.SetBackground(1, 1, 1)  # White background.
        self.vtkWidget.GetRenderWindow().AddRenderer(self.renderer)
        self.interactor = self.vtkWidget.GetRenderWindow().GetInteractor()
        
        # Add the global axis (orientation marker).
        self.axes = vtk.vtkAxesActor()
        self.orientationWidget = vtk.vtkOrientationMarkerWidget()
        self.orientationWidget.SetOrientationMarker(self.axes)
        self.orientationWidget.SetInteractor(self.interactor)
        self.orientationWidget.SetEnabled(1)
        self.orientationWidget.InteractiveOff()

        # Add the mesh objects to the renderer.
        self.add_meshes(mesh_objs, labels)
        style = vtk.vtkInteractorStyleTrackballCamera()
        self.interactor.SetInteractorStyle(style)
        # Create the left dock panel with checkboxes.
        self.create_left_panel()

        # Create menus and toolbar.
        self.create_menu()
        self.create_toolbar()

        # --- Create the Display menu for annotations ---
        # These flags and dictionaries will track whether to show:
        #  - Id annotations (node or element numbers)
        #  - Label annotations (mesh labels)
        #  - Orientation annotations (element normals)
        self.show_ids = False
        self.show_labels = False
        self.show_orientation = False
        self.id_actors = {}         # key: mesh, value: vtkActor2D for Id labels
        self.label_actors = {}      # key: mesh, value: vtkCaptionActor2D for mesh label
        self.orientation_actors = {}# key: mesh, value: vtkActor for normal glyphs
        self.create_display_menu()
        self.set_representation("Surface with Edges")
        self.renderer.ResetCamera()
        self.renderer.GetActiveCamera().AddObserver("ModifiedEvent", self.on_camera_modified)
        self.show()
        self.interactor.Initialize()
        self.compute_frustrum_planes()

    def resizeEvent(self, event):
        """avoid distortions due tu manual resizing."""
        super().resizeEvent(event)
        
        # Get current window dimensions
        window_width = self.width()
        window_height = self.height()
        window_aspect = window_width / float(window_height)
        
        camera = self.renderer.GetActiveCamera()
        
        if window_aspect > 1:
            camera.SetExplicitAspectRatio(window_aspect)
        else:
            camera.SetExplicitAspectRatio(1/window_aspect)

        self.renderer.ResetCameraClippingRange()
        self.vtkWidget.GetRenderWindow().Render()
        
    def add_meshes(self, mesh_objs, labels):
        """For each mesh, create its actor with default representation
        'Surface with Edges' and store a tuple (label, mesh, actor)."""
        for label, mesh in zip(labels, mesh_objs):
            ugrid = mesh.get_vtk_unstructured_grid()
            mapper = vtk.vtkDataSetMapper()
            mapper.SetInputData(ugrid)
            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            prop = actor.GetProperty()
            # Default representation: Surface with Edges.
            prop.SetRepresentationToSurface()
            prop.EdgeVisibilityOn()
            prop.SetOpacity(1.0)
            prop.SetColor(mesh.color)
            # Compute a contrasting edge color.
            edge_color = self.get_contrasting_color(mesh.color)
            prop.SetEdgeColor(edge_color)
            self.renderer.AddActor(actor)
            self.mesh_items.append((label, mesh, actor))

    def create_left_panel(self):
        """Create a left dock widget with a scrollable column of checkboxes.
        The docks title bar contains the 'Select All' and 'Unselect All' buttons,
        placed to the right of the title text.
        """
        # --- Create the container for the checkboxes ---
        container = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(container)
        
        # Create checkboxes for each mesh.
        self.checkboxes = []
        for label, mesh, actor in self.mesh_items:
            cb = QtWidgets.QCheckBox(label)
            cb.setChecked(True)
            cb.toggled.connect(lambda checked, a=actor: self.toggle_visibility(a, checked))
            layout.addWidget(cb)
            self.checkboxes.append(cb)
        
        layout.addStretch()
        
        # Wrap the container in a scroll area.
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidget(container)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        
        # --- Create the dock widget ---
        dock = QtWidgets.QDockWidget("Objects", self)
        dock.setWidget(scroll_area)
        
        # --- Create a custom title bar for the dock widget ---
        title_bar = QtWidgets.QWidget()
        title_layout = QtWidgets.QHBoxLayout(title_bar)
        title_layout.setContentsMargins(2, 2, 2, 2)
        
        # Add the title label.
        title_label = QtWidgets.QLabel("Objects")
        title_layout.addWidget(title_label)
        
        # Add a stretch to push buttons to the right.
        title_layout.addStretch()
        
        # "Select All" button (green check mark, 12x12).
        select_all_button = QtWidgets.QPushButton("\u2714")
        select_all_button.setToolTip("Select All")
        select_all_button.setStyleSheet("color: green; font-weight: normal;")
        select_all_button.setFixedSize(12, 12)
        select_all_button.clicked.connect(self.select_all_checkboxes)
        title_layout.addWidget(select_all_button)
        
        # "Unselect All" button (red cross mark, 12x12).
        unselect_all_button = QtWidgets.QPushButton("\u2718")
        unselect_all_button.setToolTip("Unselect All")
        unselect_all_button.setStyleSheet("color: red; font-weight: normal;")
        unselect_all_button.setFixedSize(12, 12)
        unselect_all_button.clicked.connect(self.unselect_all_checkboxes)
        title_layout.addWidget(unselect_all_button)
        
        # Set the custom title bar widget for the dock.
        dock.setTitleBarWidget(title_bar)
        
        # --- Set a minimum width for the dock ---
        # Compute maximum width among the labels.
        font = self.font()
        fm = QtGui.QFontMetrics(font)
        #max_text_width = max((fm.width(label) for label, _, _ in self.mesh_items), default=100)  # QT5
        max_text_width = max((fm.boundingRect(label).width() for label, _, _ in self.mesh_items), default=100)

        # Add some padding.
        dock.setMinimumWidth(max_text_width + 50)
        
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dock)
        
    def select_all_checkboxes(self):
        """
        Set all checkboxes in the left panel to 'checked' state.
        This will make all mesh actors visible in the viewer.
        """
        for cb in self.checkboxes:
            cb.setChecked(True)

    def unselect_all_checkboxes(self):
        """
        Set all checkboxes in the left panel to 'unchecked' state.
        This will hide all mesh actors from the viewer.
        """
        for cb in self.checkboxes:
            cb.setChecked(False)

    def toggle_visibility(self, actor, visible):
        """
        Toggle the visibility of a mesh actor.

        Parameters:
            actor (vtkActor): The VTK actor representing the mesh.
            visible (bool): If True, the actor will be visible; otherwise, it will be hidden.
        """
        actor.SetVisibility(1 if visible else 0)
        self.update_annotations()  
        self.vtkWidget.GetRenderWindow().Render()


    def create_menu(self):
        """Create the menu bar with 'Menu', 'View', and now a 'Mesh' menu."""
        menubar = self.menuBar()
        
        # Menu with Save Screenshot.
        menuMenu = menubar.addMenu("Menu")
        saveAction = QtGui.QAction("Save Screenshot", self)
        saveAction.triggered.connect(self.save_screenshot)
        menuMenu.addAction(saveAction)
        
        # View menu for camera presets.
        viewMenu = menubar.addMenu("View")
        views = ["Top", "Bottom", "Front", "Back", "Left", "Right", "Isometric"]
        for view in views:
            action = QtGui.QAction(view, self)
            action.triggered.connect(lambda checked, v=view: self.set_view(v))
            viewMenu.addAction(action)
        
        # NEW: Display mesh representation menu.
        displayMenu = menubar.addMenu("Mesh")
        displayGroup = QtGui.QActionGroup(self)
        displayGroup.setExclusive(True)
        representations = [
            ("Points", "points"),
            ("Surface", "surface"),
            ("Surface with Edges", "surface_edges"),
            ("Wireframe", "wireframe")
        ]
        for rep, key in representations:
            icon = QtGui.QIcon(_ICON_DICT.get(key, ""))
            action = QtGui.QAction(icon, rep, self)
            action.setCheckable(True)
            if rep == "Surface with Edges":
                action.setChecked(True)  # Default representation.
            # When triggered, call set_representation with the chosen representation.
            action.triggered.connect(lambda checked, rep=rep: self.set_representation(rep))
            displayMenu.addAction(action)
            displayGroup.addAction(action)

    def create_toolbar(self):
        """Create a bottom toolbar with an icon-based global axis toggle,
        an opacity slider, and a Reset View button."""
        toolbar = QtWidgets.QToolBar("Global Axis Toolbar")
        self.addToolBar(QtCore.Qt.BottomToolBarArea, toolbar)

        # Global axis toggle button.
        axis_icon = QtGui.QIcon(_ICON_DICT.get("global_axis", ""))
        self.axis_action = QtGui.QAction(axis_icon, "Toggle Global Axis", self)
        self.axis_action.setCheckable(True)
        self.axis_action.setChecked(True)
        self.axis_action.triggered.connect(self.toggle_global_axis)
        toolbar.addAction(self.axis_action)

        toolbar.addSeparator()
        
        # View reset buttons with icons
        view_buttons = [
            ("Top", "top_view"),  # Top view
            ("Left", "left_view"),  # Left view
            ("Front", "front_view"),  # Front view
            ("Isometric", "isometric_view"),  # Isometric view
        ]
    
        for view_name, icon_name in view_buttons:
            icon = QtGui.QIcon(_ICON_DICT.get(icon_name, ""))
            action = QtGui.QAction(icon, view_name, self)
            action.setToolTip(f"Set view to {view_name}")
            action.triggered.connect(lambda checked, v=view_name: self.set_view(v))
            toolbar.addAction(action)

        # Spacer.
        spacer = QtWidgets.QWidget()
        spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        toolbar.addWidget(spacer)

        # Opacity slider.
        opacity_label = QtWidgets.QLabel("Opacity:")
        toolbar.addWidget(opacity_label)
        
        self.opacity_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.opacity_slider.setMinimum(0)
        self.opacity_slider.setMaximum(100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.setFixedWidth(150)
        self.opacity_slider.valueChanged.connect(self.set_opacity)
        toolbar.addWidget(self.opacity_slider)
        
        toolbar.addSeparator()
        # Reset View button.
        reset_icon = QtGui.QIcon(_ICON_DICT.get("reset_view", ""))
        self.resetAction = QtGui.QAction(reset_icon, "Reset View", self)
        self.resetAction.setToolTip("Rezoom to show the entire scene")
        self.resetAction.triggered.connect(self.reset_view)
        toolbar.addAction(self.resetAction)

    def set_representation(self, representation):
        """Set the display representation for all mesh actors based on the selected option."""
        for label, mesh, actor in self.mesh_items:
            prop = actor.GetProperty()
            if representation == "Points":
                prop.SetRepresentationToPoints()
                prop.SetPointSize(5)
                prop.EdgeVisibilityOff()
                prop.SetOpacity(1.0)
                prop.SetColor(mesh.color)
            elif representation == "Surface":
                prop.SetRepresentationToSurface()
                prop.SetPointSize(5)
                prop.EdgeVisibilityOff()
                prop.SetOpacity(1.0)
                prop.SetColor(mesh.color)
            elif representation == "Surface with Edges":
                prop.SetRepresentationToSurface()
                prop.SetPointSize(5)
                prop.EdgeVisibilityOn()
                prop.SetOpacity(1.0)
                prop.SetColor(mesh.color)
                edge_color = self.get_contrasting_color(mesh.color)
                prop.SetEdgeColor(edge_color)
            elif representation == "Wireframe":
                prop.SetRepresentationToWireframe()
                prop.SetPointSize(5)
                prop.EdgeVisibilityOn()
                prop.SetEdgeColor(mesh.color)
                prop.SetOpacity(1.0)
        self.update_annotations()  # refresh any annotations (e.g. Id or normals) based on rep
        self.vtkWidget.GetRenderWindow().Render()

    def get_contrasting_color(self, color):
        """Return a contrasting color (black or white) based on the brightness of the input color.
            Assumes color is a tuple (r, g, b) with values in [0,1]."""
        r, g, b = color
        brightness = 0.2126 * r + 0.7152 * g + 0.0722 * b
        return (0, 0, 0) if brightness > 0.5 else (1, 1, 1)

    def set_opacity(self, value):
        """Set the opacity for all mesh actors based on the slider value."""
        opacity = value / 100.0
        for label, mesh, actor in self.mesh_items:
            actor.GetProperty().SetOpacity(opacity)
        self.vtkWidget.GetRenderWindow().Render()

    def reset_view(self):
        """Reset the camera to capture the whole scene (zoom to extents)."""
        self.renderer.ResetCamera()
        self.vtkWidget.GetRenderWindow().Render()

    def save_screenshot(self):
        """Open a file dialog to choose a filename and directory, then capture and save a screenshot as PNG."""
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save Screenshot",
            "",
            "PNG Files (*.png);;All Files (*)",
            options=options
        )
        if filename:
            if not filename.lower().endswith(".png"):
                filename += ".png"
            window = self.vtkWidget.GetRenderWindow()
            w2if = vtk.vtkWindowToImageFilter()
            w2if.SetInput(window)
            w2if.Update()
            writer = vtk.vtkPNGWriter()
            writer.SetFileName(filename)
            writer.SetInputConnection(w2if.GetOutputPort())
            writer.Write()
            QtWidgets.QMessageBox.information(self, "Screenshot",
                                              f"Screenshot saved as {filename}")

    def set_view(self, view_name):
        """Set the camera view according to the conventions and then reset the camera:
            - Top:    camera along z+ (above),    viewUp = (0, 1, 0)
            - Bottom: camera along z- (below),    viewUp = (0, -1, 0)
            - Front:   camera along y- (in front),   viewUp = (0, 0, 1)
            - Back:   camera along y+ (behind),     viewUp = (0, 0, 1)
            - Left:   camera along x- (left),       viewUp = (0, 0, 1)
            - Right:  camera along x+ (right),      viewUp = (0, 0, 1)
            - Isometric: a combination (here: x+, y-, z+), viewUp = (0, 0, 1)
        """
        camera = self.renderer.GetActiveCamera()
        focal_point = camera.GetFocalPoint()
        distance = camera.GetDistance() if camera.GetDistance() != 0 else 100

        if view_name == "Top":
            pos = (focal_point[0],
                    focal_point[1],
                    focal_point[2] + distance)
            viewUp = (0, 1, 0)
        elif view_name == "Bottom":
            pos = (focal_point[0],
                    focal_point[1],
                    focal_point[2] - distance)
            viewUp = (0, -1, 0)
        elif view_name == "Front":
            pos = (focal_point[0],
                    focal_point[1] - distance,
                    focal_point[2])
            viewUp = (0, 0, 1)
        elif view_name == "Back":
            pos = (focal_point[0],
                    focal_point[1] + distance,
                    focal_point[2])
            viewUp = (0, 0, 1)
        elif view_name == "Left":
            pos = (focal_point[0] - distance,
                    focal_point[1],
                    focal_point[2])
            viewUp = (0, 0, 1)
        elif view_name == "Right":
            pos = (focal_point[0] + distance,
                    focal_point[1],
                    focal_point[2])
            viewUp = (0, 0, 1)
        elif view_name == "Isometric":
            pos = (focal_point[0] + distance,
                    focal_point[1] - distance,
                    focal_point[2] + distance)
            viewUp = (0, 0, 1)
        else:
            return

        camera.SetPosition(pos)
        camera.SetFocalPoint(focal_point)
        camera.SetViewUp(viewUp)
        self.renderer.ResetCameraClippingRange()
        # Reset the view to rezoom the scene.
        self.reset_view()

    def toggle_global_axis(self, state):
        """Show or hide the orientation marker (global axis)."""
        self.orientationWidget.SetEnabled(1 if state else 0)
        self.vtkWidget.GetRenderWindow().Render()

    # =========================================================================
    #  Methods for the Display Menu (annotations: Id, Label, Orientation)
    # =========================================================================
    def create_display_menu(self):
        """Create a new Display menu with checkable options for:
            - Id: show the node or element numbers (depending on mesh representation)
            - Label: show the label text for the mesh
            - Orientation: show the element normals (oriented so that inside is positive)
        """
        displayMenu = self.menuBar().addMenu("Display")
        
        self.id_action = QtGui.QAction("Id", self, checkable=True)  # Qt5 = QtWidgets.QAction
        self.id_action.setChecked(False)
        self.id_action.setToolTip("Toggle display of node/element numbers")
        self.id_action.toggled.connect(self.toggle_ids)
        displayMenu.addAction(self.id_action)
        
        self.label_action = QtGui.QAction("Label", self, checkable=True)
        self.label_action.setChecked(False)
        self.label_action.setToolTip("Toggle display of mesh label")
        self.label_action.toggled.connect(self.toggle_labels)
        displayMenu.addAction(self.label_action)
        
        self.orientation_action = QtGui.QAction("Orientation", self, checkable=True)
        self.orientation_action.setChecked(False)
        self.orientation_action.setToolTip("Toggle display of element normals")
        self.orientation_action.toggled.connect(self.toggle_orientation)
        displayMenu.addAction(self.orientation_action)

    def toggle_ids(self, state):
        """
        Toggle the visibility of node/element IDs for the mesh.

        Parameters:
            state (bool): If True, display IDs; otherwise, hide them.
        """
        self.show_ids = state
        self.update_annotations()
        self.vtkWidget.GetRenderWindow().Render()

    def toggle_labels(self, state):
        """
        Toggle the visibility of mesh labels.

        Parameters:
            state (bool): If True, display labels; otherwise, hide them.
        """
        self.show_labels = state
        self.update_annotations()
        self.vtkWidget.GetRenderWindow().Render()

    def toggle_orientation(self, state):
        """
        Toggle the visibility of element orientation (normals) for the mesh.

        Parameters:
            state (bool): If True, display orientation; otherwise, hide it.
        """
        self.show_orientation = state
        self.update_annotations()
        self.vtkWidget.GetRenderWindow().Render()


    def update_annotations(self):
        """Update (add or remove) extra annotation actors (for Ids, labels, normals)
            on each visible mesh.
        """
        for label, mesh, actor in self.mesh_items:
            # Only process if the mesh actor is visible.
            if actor.GetVisibility():
                # --- Update Id annotations ---
                if self.show_ids:
                    if mesh in self.id_actors:
                        self.renderer.RemoveActor(self.id_actors[mesh])
                        del self.id_actors[mesh]
                    id_actor = self.create_id_actor(mesh, actor)
                    self.renderer.AddActor(id_actor)
                    self.id_actors[mesh] = id_actor
                else:
                    if mesh in self.id_actors:
                        self.renderer.RemoveActor(self.id_actors[mesh])
                        del self.id_actors[mesh]
                # --- Update Label annotations ---
                if self.show_labels:
                    if mesh in self.label_actors:
                        self.renderer.RemoveActor(self.label_actors[mesh])
                        del self.label_actors[mesh]
                    label_actor = self.create_label_actor(mesh, label)
                    self.renderer.AddActor(label_actor)
                    self.label_actors[mesh] = label_actor
                else:
                    if mesh in self.label_actors:
                        self.renderer.RemoveActor(self.label_actors[mesh])
                        del self.label_actors[mesh]
                # --- Update Orientation annotations ---
                # Only add normal glyphs if representation is not Points.
                rep = actor.GetProperty().GetRepresentation()
                if self.show_orientation and rep != vtk.VTK_POINTS:
                    if mesh in self.orientation_actors:
                        self.renderer.RemoveActor(self.orientation_actors[mesh])
                        del self.orientation_actors[mesh]
                    orientation_actor = self.create_orientation_actor(mesh)
                    self.renderer.AddActor(orientation_actor)
                    self.orientation_actors[mesh] = orientation_actor
                else:
                    if mesh in self.orientation_actors:
                        self.renderer.RemoveActor(self.orientation_actors[mesh])
                        del self.orientation_actors[mesh]
            else:
                # Remove any annotations if the mesh is not visible.
                if mesh in self.id_actors:
                    self.renderer.RemoveActor(self.id_actors[mesh])
                    del self.id_actors[mesh]
                if mesh in self.label_actors:
                    self.renderer.RemoveActor(self.label_actors[mesh])
                    del self.label_actors[mesh]
                if mesh in self.orientation_actors:
                    self.renderer.RemoveActor(self.orientation_actors[mesh])
                    del self.orientation_actors[mesh]

    def create_id_actor(self, mesh, mesh_actor):
        """
        Create an actor that displays the node IDs (if Points) or cell IDs (otherwise).
        
        For points:
          - Labels are placed at the point positions.
          
        For cells:
          - The cell centers are computed and labels are placed at those centers.
        """
         
        selected_ugrid = self._random_resampling(mesh)
        
        idFilter = vtk.vtkIdFilter()
        idFilter.SetInputData(selected_ugrid)

    
        # Decide whether to label point IDs or cell IDs.
        rep = mesh_actor.GetProperty().GetRepresentation()
        if rep == vtk.VTK_POINTS:
            idFilter.PointIdsOn()
            idFilter.CellIdsOff()
            idFilter.Update()
            # For points, we can use the output of the filter directly.
            labelInputConnection = idFilter.GetOutputPort()
            # We'll tell the mapper to use the point ID array.
            labelAssociation = vtk.vtkDataObject.FIELD_ASSOCIATION_POINTS
            idArrayName = "vtkIdFilterPointIds"
        else:
            idFilter.PointIdsOff()
            idFilter.CellIdsOn()
            idFilter.Update()
            # For cells, compute the center of each cell so that the label appears at the center.
            cellCenters = vtk.vtkCellCenters()
            cellCenters.SetInputConnection(idFilter.GetOutputPort())
            cellCenters.Update()
            labelInputConnection = cellCenters.GetOutputPort()
            # After vtkCellCenters, the computed centers become the point locations.
            labelAssociation = vtk.vtkDataObject.FIELD_ASSOCIATION_POINTS
            idArrayName = "vtkIdFilterCellIds"
    
        # Create the labeled data mapper.
        labelMapper = vtk.vtkLabeledDataMapper()
        labelMapper.SetInputConnection(labelInputConnection)
        labelMapper.SetLabelModeToLabelIds()
        # Explicitly tell the mapper which id array to use.
        labelMapper.SetInputArrayToProcess(0, 0, 0, labelAssociation, idArrayName)
    
        # Customize the label appearance.
        textProp = labelMapper.GetLabelTextProperty()
        textProp.SetColor(0, 0, 0)
        textProp.BoldOn()
    
        # Create a 2D actor for the labels.
        id_actor = vtk.vtkActor2D()
        id_actor.SetMapper(labelMapper)
    
        return id_actor
    
    def create_label_actor(self, mesh, text):
        """Create a caption actor to display the mesh label at the center of its bounds."""
        ugrid = mesh.get_vtk_unstructured_grid()
        bounds = ugrid.GetBounds()  # (xmin, xmax, ymin, ymax, zmin, zmax)
        x = (bounds[0] + bounds[1]) / 2.0
        y = (bounds[2] + bounds[3]) / 2.0
        z = (bounds[4] + bounds[5]) / 2.0
    
        caption = vtk.vtkCaptionActor2D()
        caption.SetCaption(text)
        caption.SetAttachmentPoint(x, y, z)
    
        # Control the overall size of the label (the text "box") in normalized viewport coords:
        caption.SetHeight(0.065)      # Try smaller or larger values to suit your preference
        # caption.SetWidth(0.1)     # If you also want to manually specify the width
    
        # You can still tweak text properties, but the above height/width typically dominates
        caption.GetCaptionTextProperty().SetColor(0, 0, 0)
        caption.GetCaptionTextProperty().BoldOn()
        caption.GetCaptionTextProperty().SetFontSize(12)  # May still have some effect, but often overridden by auto-scaling
    
        return caption

    def create_orientation_actor(self, mesh):
        """
        Create an actor that shows the orientation of mesh elements with glyphs (arrows).
    
        Behavior depends on the element dimension:
          - 0D (points): Returns an empty actor.
          - 1D (lines):  Glyphs are placed at the cell centers, pointing along the line (from the first endpoint to the second).
          - 2D (surfaces): Glyphs are placed at cell centers (of the surface) and oriented with the surface normal.
                          Normals are computed so that "positive" indicates outward.
          - 3D (volumes):  The outer surface is extracted and normals are computed similarly.
                          Glyphs are placed at the cell centers of the surface.
        """                
        ugrid = mesh.get_vtk_unstructured_grid()
        
        if ugrid.GetNumberOfCells() == 0:
            # Nothing to show
            return vtk.vtkActor()
    
        # Determine the dimension of the elements by inspecting the first cell.
        firstCell = ugrid.GetCell(0)
        cellDim = firstCell.GetCellDimension()
    
        # CASE 0D: Points -- no orientation glyphs.
        if cellDim == 0:
            return vtk.vtkActor()  # Return an empty actor.
    
        # Set a common scale factor based on the overall bounding box.
        bounds = ugrid.GetBounds()
        diag = ((bounds[1]-bounds[0])**2 +
                (bounds[3]-bounds[2])**2 +
                (bounds[5]-bounds[4])**2) ** 0.5
        scaleFactor = diag * 0.05  # adjust as needed
    
        if cellDim == 1:
            # -------------------------------
            # 1D elements: use line direction (tangent)
            # -------------------------------
            # We'll compute for each cell the center and the direction.
            ugrid = self._random_resampling(mesh)
            points = vtk.vtkPoints()
            vectors = vtk.vtkDoubleArray()
            vectors.SetNumberOfComponents(3)
            vectors.SetName("Tangent")
    
            numCells = ugrid.GetNumberOfCells()
            for i in range(numCells):
                cell = ugrid.GetCell(i)
                pts = cell.GetPoints()
                npts = pts.GetNumberOfPoints()
                # For a line or poly-line, we compute a simple tangent.
                # For simplicity, we'll take the vector from the first point to the last point.
                p0 = pts.GetPoint(0)
                pN = pts.GetPoint(npts-1)
                center = [(p0[j] + pN[j]) * 0.5 for j in range(3)]
                points.InsertNextPoint(center)
                # Compute direction vector and normalize.
                direction = [pN[j] - p0[j] for j in range(3)]
                norm = (direction[0]**2 + direction[1]**2 + direction[2]**2) ** 0.5
                if norm > 0:
                    direction = [direction[j] / norm for j in range(3)]
                else:
                    direction = [0.0, 0.0, 0.0]
                vectors.InsertNextTuple(direction)
    
            # Create a polydata to hold the centers and direction vectors.
            polyData = vtk.vtkPolyData()
            polyData.SetPoints(points)
            polyData.GetPointData().SetVectors(vectors)
    
            # Create an arrow source.
            arrowSource = vtk.vtkArrowSource()
    
            # Glyph the arrow at each center with the computed direction.
            glyph = vtk.vtkGlyph3D()
            glyph.SetSourceConnection(arrowSource.GetOutputPort())
            glyph.SetInputData(polyData)
            glyph.SetVectorModeToUseVector()
            glyph.SetScaleFactor(scaleFactor)
            glyph.Update()
    
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(glyph.GetOutputPort())
            arrowActor = vtk.vtkActor()
            arrowActor.SetMapper(mapper)
            arrowActor.GetProperty().SetColor(1, 0, 0)  # red arrows
            return arrowActor
    
        elif cellDim == 2 or cellDim == 3:
            if cellDim == 2:
                ugrid = self._random_resampling(mesh)
            # -------------------------------
            # 2D (surface) or 3D (volume) elements: use surface normals.
            # -------------------------------
            # Extract the outer surface.
            surfaceFilter = vtk.vtkDataSetSurfaceFilter()
            surfaceFilter.SetInputData(ugrid)
            surfaceFilter.Update()
            polyData = surfaceFilter.GetOutput()
    
            # radomize surface element
            if cellDim == 3:
                surface_ug_filter = vtk.vtkPolyDataToUnstructuredGrid()
                surface_ug_filter.AddInputData(polyData)
                surface_ug_filter.Update()
                surface_ug_displayed = self._random_resampling(surface_ug_filter.GetOutput())
                surfaceFilter2 = vtk.vtkDataSetSurfaceFilter()
                surfaceFilter2.SetInputData(surface_ug_displayed)
                surfaceFilter2.Update()
                polyData = surfaceFilter2.GetOutput()
            # Compute normals on the surface.
            normalsFilter = vtk.vtkPolyDataNormals()
            normalsFilter.SetInputData(polyData)
            normalsFilter.ComputeCellNormalsOn()
            normalsFilter.ComputePointNormalsOff()
            normalsFilter.SetConsistency(1)
            normalsFilter.AutoOrientNormalsOff()
    
            # If the orientation is negative (clockwise), we flip the normals
            normalsFilter.Update()  # Recompute normals after orientation reversal
            if cellDim==3 and self._calculate_orientation(mesh) < 0:
                normalsFilter.FlipNormalsOn()  # Flip the normals to make them point inward
                normalsFilter.Update()  # Recompute normals after orientation reversal
            polyDataWithNormals = normalsFilter.GetOutput()
    
            # Compute cell centers for placing the glyphs.
            cellCenters = vtk.vtkCellCenters()
            cellCenters.SetInputData(polyDataWithNormals)
            cellCenters.Update()
    
            # Create arrow glyphs oriented by the normals.
            arrowSource = vtk.vtkArrowSource()
            glyph = vtk.vtkGlyph3D()
            glyph.SetSourceConnection(arrowSource.GetOutputPort())
            glyph.SetInputConnection(cellCenters.GetOutputPort())
            glyph.SetVectorModeToUseNormal()
            glyph.SetScaleFactor(scaleFactor)
            glyph.Update()
    
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(glyph.GetOutputPort())
            arrowActor = vtk.vtkActor()
            arrowActor.SetMapper(mapper)
            arrowActor.GetProperty().SetColor(1, 0, 0)  # red arrows
            return arrowActor
    
        else:
            # If for some reason we get an unexpected dimension, return an empty actor.
            return vtk.vtkActor()

    def _random_resampling(self, mesh):
        """
        Perform random resampling of the input mesh by selecting a subset of cells.

        Parameters:
            mesh (vtk.vtkUnstructuredGrid or Mesh): The input mesh to resample.

        Returns:
            vtkUnstructuredGrid: A new grid containing the randomly selected cells.
        """
        if isinstance(mesh, vtk.vtkUnstructuredGrid):
            original_grid = mesh  # Original unstructured grid
        else:
            original_grid = mesh.get_vtk_unstructured_grid()  # Original unstructured grid
            
        clipped_grid = self._clip_ugrid_with_planes(original_grid)
        num_cells = clipped_grid.GetNumberOfCells()
        
        # Define the number of cells to display (randomly sampled)
        num_sample_cells = min(_MAX_ITEM_DISPLAYED // len(self.mesh_items), num_cells)
        
        # Select cells randomly from the available cells
        selected_cell_ids = random.sample(range(num_cells), num_sample_cells)
        points, cells, types = vtk_to_numpy_connectivity(clipped_grid)
        selected_cell_ids = np.array(random.sample(range(len(cells)), num_sample_cells))
        selected_cells = [cells[i] for i in selected_cell_ids]
        selected_types = np.take(types, selected_cell_ids, axis=0)
        selected_points_ids = np.unique(np.concatenate(selected_cells))
        selected_points = np.take(points, selected_points_ids, axis=0)
        point_id_to_new_index = {selected_points_ids[i]: np.int64(i) for i in range(len(selected_points_ids))}
        for i in range(len(selected_cells)):
            for j in range(len(selected_cells[i])):
                selected_cells[i][j] = point_id_to_new_index[selected_cells[i][j]]
        
        # Create a new grid to hold the selected cells
        return numpy_to_vtk_connectivity(selected_points, selected_cells, selected_types)

    def _clip_ugrid_with_plane(self, ugrid, clip_plane, inside=True, boundary=True):
        """
        Clip the input unstructured grid with a single clipping plane.

        Parameters:
            ugrid (vtk.vtkUnstructuredGrid): The unstructured grid to clip.
            clip_plane (vtk.vtkPlane): The clipping plane used for the operation.
            inside (bool): If True, extracts the part of the grid inside the plane.
            boundary (bool): If True, extracts boundary cells.

        Returns:
            vtk.vtkUnstructuredGrid: The clipped unstructured grid.
        """
        # Set up the extract geometry filter
        extract_geom = vtkExtractGeometry()
        extract_geom.SetInputData(ugrid)
        extract_geom.SetImplicitFunction(clip_plane)
        if inside:
            extract_geom.ExtractInsideOn()
        else:
            extract_geom.ExtractInsideOff()
        if boundary:
            extract_geom.ExtractBoundaryCellsOn()
        else:
            extract_geom.ExtractBoundaryCellsOff()
        
        # Execute the extraction process
        extract_geom.Update()
        return extract_geom.GetOutput()

    def _clip_ugrid_with_planes(self, ugrid):
        """
        Clips the given unstructured grid using the frustum planes stored in self.vtk_planes.

        Parameters:
            ugrid (vtk.vtkUnstructuredGrid): The unstructured grid to clip.

        Returns:
            vtk.vtkUnstructuredGrid: The final clipped unstructured grid.
        """
        clipped_ugrid = ugrid  # Start with the input unstructured grid
        
        # Apply the clipping planes sequentially
        for plane in self.vtk_planes:
            clipped_ugrid = self._clip_ugrid_with_plane(clipped_ugrid, plane, inside=False)
        
        # Return the final clipped unstructured grid
        return clipped_ugrid

    def _calculate_orientation(self, mesh):
        """
        Calculate the orientation of the first cell in the mesh by determining the normal direction.

        Parameters:
            mesh (Mesh): The input mesh for which the orientation is calculated.

        Returns:
            int: 1 if the normal points towards the centroid (counterclockwise), -1 if it points away (clockwise).
        """
        pts, cells, _ = vtk_to_numpy_connectivity(mesh.get_vtk_unstructured_grid())
        # Extract the vertices from the cell
        vertices = pts[cells[0]]
        
        # Create vectors from the first three points of the triangle (assuming a 3D polygon)
        vec1 = vertices[1] - vertices[0]
        vec2 = vertices[2] - vertices[0]
        
        # Compute the cross product to get the normal vector
        normal = np.cross(vec1, vec2)
        centroid_cell = np.mean(pts, axis=0)
        centroid_face = np.mean(vertices, axis=0)
        normal_to_centroid = centroid_cell - centroid_face
        dot_product = np.dot(normal, normal_to_centroid)
        
        # Return the sign of the dot product to determine the orientation (counterclockwise or clockwise)
        return np.sign(dot_product)

    def on_camera_modified(self, obj, event):
        """
        Triggered when the camera is modified (e.g., zoom, rotate).

        This method updates the frustum planes based on the new camera position.
        """
        self.compute_frustrum_planes()

    def compute_frustrum_planes(self):
        """
        Compute the frustum planes based on the current camera view.

        This method stores the planes in self.vtk_planes, which are used to clip the mesh.
        """
        # Get the current camera from the renderer
        camera = self.renderer.GetActiveCamera()
        planes = [0.0] * 24
        
        # Retrieve the frustum planes from the camera
        camera.SetUseExplicitAspectRatio(True)
        camera.GetFrustumPlanes(1.0, planes)
        self.vtk_planes = []
        
        # Loop through the 6 frustum planes and extract the coefficients
        for i in range(6):
            a = planes[4*i]
            b = planes[4*i+1]
            c = planes[4*i+2]
            d = planes[4*i+3]

            if a != 0:
                x = -d / a
                point_on_plane = [x, 0, 0]
            elif b != 0:
                y = -d / b
                point_on_plane = [0, y, 0]
            elif c != 0:
                z = -d / c
                point_on_plane = [0, 0, z]
            else:
                raise ValueError("The coefficients a, b, and c cannot all be zero. Invalid plane.")
            
            # Create a vtkPlane object and store it in vtk_planes
            plane = vtk.vtkPlane()
            plane.SetNormal(a, b, c)
            plane.SetOrigin(point_on_plane)
            self.vtk_planes.append(plane)

    