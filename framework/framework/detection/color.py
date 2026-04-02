"""
Color-based contour detection — direct port of ChromaScape ColourContours.java.

Pipeline: BGR → HSV → inRange mask → morphological close → findContours
→ pick closest-to-center → rejection-sample random point inside contour.
"""

import random
import logging
import cv2
import numpy as np

from framework.colors import ColorRange

logger = logging.getLogger(__name__)

# Pre-built morphological kernels (matching ChromaScape 20×20 ellipse)
_DILATE_KERNEL = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (20, 20))
_ERODE_KERNEL  = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (20, 20))


class ColorDetector:
    """
    Finds colored game elements in a BGR screenshot using HSV thresholding.

    All pixel coordinates returned are relative to the image origin (canvas-relative
    when the image is a full canvas capture).
    """

    def get_contours_in_color(
        self, image: np.ndarray, color: ColorRange
    ) -> list[np.ndarray]:
        """
        Return a list of contours (each an Nx1x2 int32 array) matching the given
        HSV color range in the BGR image.
        """
        mask = self._extract_mask(image, color)
        mask = self._morph_close(mask)
        contours, _ = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        return list(contours)

    def get_contour_closest_to_center(
        self, contours: list[np.ndarray], image_shape: tuple
    ) -> np.ndarray | None:
        """
        Return the contour whose centroid is closest to the image center.
        """
        if not contours:
            return None

        h, w = image_shape[:2]
        cx, cy = w / 2, h / 2
        best = None
        best_dist = float("inf")

        for contour in contours:
            M = cv2.moments(contour)
            if M["m00"] == 0:
                continue
            mx = M["m10"] / M["m00"]
            my = M["m01"] / M["m00"]
            dist = (mx - cx) ** 2 + (my - cy) ** 2
            if dist < best_dist:
                best_dist = dist
                best = contour

        return best

    def random_point_in_contour(
        self, contour: np.ndarray, max_attempts: int = 15
    ) -> tuple[int, int] | None:
        """
        Rejection-sample a random point that lies inside the contour.
        Returns (x, y) or None if max_attempts exceeded.
        """
        x, y, w, h = cv2.boundingRect(contour)
        for _ in range(max_attempts):
            rx = random.randint(x, x + w - 1)
            ry = random.randint(y, y + h - 1)
            if cv2.pointPolygonTest(contour, (float(rx), float(ry)), False) >= 0:
                return rx, ry
        return None

    def get_random_point_in_color(
        self,
        image: np.ndarray,
        color: ColorRange,
        max_attempts: int = 15,
        debug: bool = False,
        debug_save_path: str | None = None,
    ) -> tuple[int, int] | None:
        """
        High-level helper: find the closest-to-center contour in the given color,
        then return a random point inside it.

        In debug mode, saves an annotated screenshot to debug_save_path (if provided):
        - Contour outlines drawn in green
        - Chosen point marked with a red dot
        - Logs HSV mask coverage percentage
        """
        contours = self.get_contours_in_color(image, color)

        if debug:
            mask = self._extract_mask(image, color)
            coverage = np.count_nonzero(mask) / mask.size * 100
            logger.debug(
                "HSV mask coverage for '%s': %.2f%% (%d contours found)",
                color.name, coverage, len(contours),
            )

        if not contours:
            if debug:
                logger.debug("No contours found for color '%s'", color.name)
            return None

        best = self.get_contour_closest_to_center(contours, image.shape)
        if best is None:
            return None

        point = self.random_point_in_contour(best, max_attempts)

        if debug and debug_save_path is not None:
            self._save_debug_image(image, contours, best, point, debug_save_path)

        return point

    # ------------------------------------------------------------------ helpers

    @staticmethod
    def _extract_mask(image: np.ndarray, color: ColorRange) -> np.ndarray:
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lower = np.array(color.hsv_min, dtype=np.uint8)
        upper = np.array(color.hsv_max, dtype=np.uint8)
        return cv2.inRange(hsv, lower, upper)

    @staticmethod
    def _morph_close(mask: np.ndarray) -> np.ndarray:
        """
        Morphological closing: dilate → fill contours → erode.
        Matches the ChromaScape morphClose() logic exactly.
        """
        dilated = cv2.morphologyEx(mask, cv2.MORPH_DILATE, _DILATE_KERNEL)
        # Fill all external contours with white for consistency
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(dilated, contours, -1, 255, -1)
        eroded = cv2.morphologyEx(dilated, cv2.MORPH_ERODE, _ERODE_KERNEL)
        return eroded

    @staticmethod
    def _save_debug_image(
        image: np.ndarray,
        contours: list[np.ndarray],
        best_contour: np.ndarray,
        point: tuple[int, int] | None,
        save_path: str,
    ) -> None:
        import os
        annotated = image.copy()
        # All contours in green
        cv2.drawContours(annotated, contours, -1, (0, 255, 0), 2)
        # Best contour outline in brighter green
        cv2.drawContours(annotated, [best_contour], -1, (0, 255, 128), 3)
        # Chosen point as red dot
        if point is not None:
            cv2.circle(annotated, point, 6, (0, 0, 255), -1)
            cv2.circle(annotated, point, 8, (255, 255, 255), 1)
        os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else ".", exist_ok=True)
        cv2.imwrite(save_path, annotated)
        logger.debug("Debug image saved: %s", save_path)
