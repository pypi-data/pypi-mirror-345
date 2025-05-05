#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ghahreman - A PyVista-based 3D trophy visualization tool.

This module creates a golden trophy with two cones connected at their vertices,
with the upper cone being larger than the lower one. The trophy includes decorative
elements such as disks, a base, spheres, and handles, all rendered in a golden color.

A package for champion (ghahreman) from master (ostad).
"""

import pyvista as pv
import numpy as np


class Hero:
    """
    A class for creating and displaying a golden trophy.

    This class follows SOLID principles and provides functionality to create,
    configure, and display a golden trophy composed of two cones connected at
    their vertices, with decorative elements such as disks, a base, spheres,
    and handles.
    """

    def __init__(self, height1=1.0, radius1=0.5, height2=None, radius2=None, resolution=30,
                 disk_radius=None, disk_thickness=0.1, bottom_disk_radius=None, bottom_disk_thickness=0.3,
                 cube_size=None, cube_height=0.5, sphere_radius=None, handle_thickness=None):
        """
        Initialize the Hero class.

        Parameters
        ----------
        height1 : float
            Height of the upper cone
        radius1 : float
            Base radius of the upper cone
        height2 : float, optional
            Height of the lower cone (if None, set to one-third of the upper cone's height)
        radius2 : float, optional
            Base radius of the lower cone (if None, set to 80% of the upper cone's radius)
        resolution : int
            Resolution (number of segments) for the cones and other elements
        disk_radius : float, optional
            Radius of the horizontal disk at the connection point of the two cones
            (if None, set to the average of the two cones' radii)
        disk_thickness : float
            Thickness of the horizontal disk at the connection point
        bottom_disk_radius : float, optional
            Radius of the horizontal disk below the lower cone
            (if None, set to the lower cone's radius)
        bottom_disk_thickness : float
            Thickness of the horizontal disk below the lower cone
        cube_size : float, optional
            Size of the cube below the bottom disk
            (if None, set to 1.5 times the bottom disk's radius)
        cube_height : float
            Height of the cube below the bottom disk
        sphere_radius : float, optional
            Radius of the small sphere tangent to the upper cone's base
            (if None, set to one-fifth of the upper cone's radius)
        handle_thickness : float, optional
            Thickness of the trophy handles
            (if None, set to one-tenth of the upper cone's radius)
        """
        self.height1 = height1
        self.radius1 = radius1
        self.height2 = height2 if height2 is not None else height1 / 3.0
        self.radius2 = radius2 if radius2 is not None else radius1 * 0.8  # 20% smaller
        self.resolution = resolution
        self.disk_radius = disk_radius if disk_radius is not None else (self.radius1 + self.radius2) / 2
        self.disk_thickness = disk_thickness
        self.bottom_disk_radius = bottom_disk_radius if bottom_disk_radius is not None else self.radius2
        self.bottom_disk_thickness = bottom_disk_thickness
        self.cube_size = cube_size if cube_size is not None else self.bottom_disk_radius * 1.5
        self.cube_height = cube_height
        self.sphere_radius = sphere_radius if sphere_radius is not None else self.radius1 * 0.2  # One-fifth of the upper cone's base radius
        self.handle_thickness = handle_thickness if handle_thickness is not None else self.radius1 * 0.1  # One-tenth of the upper cone's base radius
        self.cone1 = None
        self.cone2 = None
        self.disk = None
        self.bottom_disk = None
        self.cube = None
        self.sphere = None
        self.upper_sphere = None  # Second sphere at a higher position
        self.handle1 = None  # First trophy handle
        self.handle2 = None  # Second trophy handle
        self.plotter = None

        # Create the cones, horizontal disks, cube, spheres, and handles
        self._create_cones()

    def _create_cones(self):
        """
        Create two cones with their vertices connected and a horizontal disk at the connection point.

        This method creates two cones with their vertices connected, facing in opposite directions.
        The upper cone is larger than the lower one. It also creates a horizontal disk at the
        connection point of the two cones, as well as other decorative elements like a base,
        spheres, and handles.
        """
        # Create the upper (larger) cone using PyVista
        # Center of the cone is at (0, 0, 0) and its direction is upward (positive z-axis)
        self.cone1 = pv.Cone(center=(0, 0, 0),
                            direction=(0, 0, 1),
                            height=self.height1,
                            radius=self.radius1,
                            resolution=self.resolution)

        # Rotate the upper cone 180 degrees to place it on its vertex
        # This makes the vertex of the cone at (0, 0, 0) and its base in the negative z direction
        rotation_matrix = np.array([
            [1, 0, 0],
            [0, -1, 0],
            [0, 0, -1]
        ])
        self.cone1.transform(rotation_matrix, inplace=True)

        # In PyVista, a cone is created by default with its base center at the specified center
        # and its vertex at a distance of 'height' in the specified direction.
        # After rotation, the vertex of the upper cone is at (0, 0, 0) and its base is in the negative z direction.

        # Create the lower (smaller) cone using PyVista
        # The lower cone should be in the opposite direction of the upper cone (downward)
        # First, create the cone at center (0, 0, -1)
        self.cone2 = pv.Cone(center=(0, 0, -1),
                            direction=(0, 0, 1),  # Direction is upward (positive z-axis)
                            height=self.height2,
                            radius=self.radius2,
                            resolution=self.resolution)

        # Then translate the lower cone downward so that its vertex connects to the vertex of the upper cone
        # and it goes further down by its own height
        # The vertex of the cone is at a distance of 'height' from the base center
        # So we need to translate the cone by height*7 in the negative z direction
        # (This specific multiplier was determined experimentally for optimal positioning)
        self.cone2.translate((0, 0, -self.height2 * 7))

        # Create a horizontal disk at the connection point of the two cones
        # We use a cylinder with a small height as a disk
        self.disk = pv.Cylinder(
            center=(0, 0, -0.8),  # Center of the disk at the connection point of the two cones
            direction=(0, 0, 1),  # Direction is upward (positive z-axis)
            height=self.disk_thickness,  # Height (thickness) of the disk
            radius=self.disk_radius * 0.2,  # Radius of the disk
            resolution=self.resolution  # Resolution of the disk
        )

        # Translate the disk to the appropriate position (half of its thickness above the connection point and half below)
        self.disk.translate((0, 0, -self.disk_thickness/2))

        # Create a second horizontal disk below the lower cone (at the base of the lower cone)
        # Calculate the z position for the base of the lower cone
        # The lower cone is at position z = -self.height2 * 1.2 and its height is self.height2
        # So its base is at position z = -self.height2 * 1.2 - self.height2
        bottom_disk_z = -self.height2 * 1.2 - self.height2

        # Create the second horizontal disk
        self.bottom_disk = pv.Cylinder(
            center=(0, 0, bottom_disk_z),  # Center of the disk at the base of the lower cone
            direction=(0, 0, 1),  # Direction is upward (positive z-axis)
            height=self.bottom_disk_thickness * 0.9,  # Height (thickness) of the disk
            radius=self.bottom_disk_radius * 1.2,  # Radius of the disk
            resolution=self.resolution  # Resolution of the disk
        )

        # Create a cube below the bottom disk
        # Calculate the z position for the cube
        # The bottom disk is at position z = bottom_disk_z and its thickness is self.bottom_disk_thickness
        # So the bottom of the disk is at position z = bottom_disk_z - self.bottom_disk_thickness/2
        # And the cube should start from there
        cube_z = bottom_disk_z - self.bottom_disk_thickness/2 - self.cube_height/2

        # Create the cube
        # In PyVista, a cube is created using Box, which requires specifying its bounds
        # Bounds are defined for each dimension as (min, max)
        half_size = self.cube_size / 2
        self.cube = pv.Box(
            bounds=(-half_size * 1.8, half_size * 1.8,  # Bounds in the x direction
                   -half_size * 1.9, half_size * 1.9,   # Bounds in the y direction
                   cube_z - self.cube_height/2, cube_z + self.cube_height/2)  # Bounds in the z direction
        )

        # Create a small sphere tangent to the base of the upper cone
        # Calculate the z position for the sphere
        # The base of the upper cone is at position z = -self.height1 (after rotation)
        # For the sphere to be tangent to the base, its center should be at a distance of its radius from the base
        sphere_z = self.height1 * 0.3 - self.sphere_radius

        # Create the sphere
        self.sphere = pv.Sphere(
            radius=self.sphere_radius * 3.4,
            center=(0, 0, sphere_z),  # Center of the sphere on the z-axis, tangent to the base of the upper cone
            theta_resolution=self.resolution,
            phi_resolution=self.resolution
        )

        # Create a second sphere at a higher position
        # This sphere is similar to the first one, but positioned higher
        # We place the second sphere higher than the first one
        upper_sphere_z = sphere_z + self.height1 * 0.1  # Higher position than the first sphere

        # Create the second sphere
        self.upper_sphere = pv.Sphere(
            radius=self.sphere_radius * 4,  # Similar radius to the first sphere
            center=(0, 0, upper_sphere_z),  # Center of the sphere at a higher position
            theta_resolution=self.resolution,
            phi_resolution=self.resolution
        )

        # Create the trophy handles
        # The handles are curved and positioned on both sides of the trophy
        # To create the curve, we use a spline path and then convert it to a tube

        # Determine the position of the handles
        # The handles should start from the middle of the upper cone, curve upward and outward,
        # and then curve back downward and inward to connect back to the middle of the upper cone

        # Start and end position of the handles (at the middle height of the upper cone)
        handle_z = -self.height1 / 2  # Middle height of the upper cone
        handle_radius = self.radius1 * .8  # Handle radius (slightly smaller than the upper cone's base radius)

        # Create path points for the first handle (right side)
        # The path starts from the right side, curves upward and outward, and then curves back downward and inward
        handle1_points = []
        n_points = 20  # Number of path points

        for i in range(n_points):
            t = i / (n_points - 1)  # Parameter between 0 and 1
            angle = np.pi * t  # Angle from 0 to π

            # Calculate x, y, z position for each path point
            x = handle_radius * np.sin(angle) * .9 * -1
            y = handle_radius * np.sin(angle) * .9 * -1  # Compression in the y direction
            z = handle_z * 0.01 + 1.4 * handle_radius * np.cos(angle)  # Curve in the z direction

            handle1_points.append([x, y, z])

        # Convert points to a NumPy array
        handle1_points = np.array(handle1_points)

        # Create a spline curve for the first handle
        handle1_spline = pv.Spline(handle1_points, n_points * 12)

        # Convert the path to a tube
        self.handle1 = handle1_spline.tube(radius=self.handle_thickness * .6, n_sides=self.resolution)

        # Create the second handle (left side) by mirroring the first handle
        self.handle2 = self.handle1.copy()

        # Mirror the second handle in the x and y directions
        self.handle2.points[:, 1] *= -1
        self.handle2.points[:, 0] *= -1

    def display(self, background_color="white", window_size=(800, 600)):
        """
        Display the golden trophy in a window.

        Parameters
        ----------
        background_color : str
            Background color of the display window
        window_size : tuple
            Size of the display window (width, height)
        """
        # Create a display window
        self.plotter = pv.Plotter(window_size=window_size)
        self.plotter.set_background(background_color)

        # Set the color of the trophy to golden
        # Golden color with RGB code: (255, 215, 0) or in [0, 1] scale: (1.0, 0.843, 0.0)
        golden_color = (1.0, 0.843, 0.0)

        # Add the cones, horizontal disks, cube, spheres, and handles to the display window with golden color
        self.plotter.add_mesh(self.cone1, color=golden_color, specular=1.0, specular_power=15)
        self.plotter.add_mesh(self.cone2, color=golden_color, specular=1.0, specular_power=15)
        self.plotter.add_mesh(self.disk, color="#9c9c9c", specular=1.0, specular_power=15)
        self.plotter.add_mesh(self.bottom_disk, color="#9c9c9c", specular=1.0, specular_power=15)
        self.plotter.add_mesh(self.cube, color="#472a07", specular=1.0, specular_power=15)
        self.plotter.add_mesh(self.sphere, color=golden_color, specular=1.0, specular_power=15)
        self.plotter.add_mesh(self.upper_sphere, color=golden_color, specular=1.0, specular_power=15)
        self.plotter.add_mesh(self.handle1, color=golden_color, specular=1.0, specular_power=15)
        self.plotter.add_mesh(self.handle2, color=golden_color, specular=1.0, specular_power=15)

        # Add the text "Stay Champion Forever" to the image
        # Position the text in front of the trophy
        text_position = (0, -self.radius1 * 2, -self.height1 * 0.5)  # Position of the text in front of the trophy
        self.plotter.add_text("Stay Champion Forever", position=text_position, font_size=24, color='black',
                             shadow=True, name='trophy_text', font='arial')

        # Display the window
        self.plotter.show()


def main():
    """
    Main function to create and display the golden trophy.

    This function creates an instance of the Hero class with specific
    parameters and displays the resulting golden trophy.
    """
    # Create an instance of the Hero class
    # Upper cone with height 2.0 and radius 1.0
    # Lower cone with height 2.0/3 = 0.67 and radius 0.8
    hero = Hero(height1=2.0, radius1=1.0, resolution=60)

    # Display the trophy
    hero.display(background_color="white", window_size=(1000, 800))


if __name__ == "__main__":
    main()
