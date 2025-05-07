from __future__ import annotations
from functools import cached_property
import cv2
from typing import List, Tuple, Optional
import numpy as np
from pathlib import Path
from typing import Union

from .exceptions import InvalidParameterError, UnsupportedSymbolError

__all__ = ["AztecMatrix"]


class AztecMatrix:
    """Convert a *cropped* Aztec-code image into a binary module matrix.

    The extractor assumes the image already contains **only** the Aztec
    symbol (no perspective skew, no surrounding background).

    Parameters
    ----------
    image_path : Union[str, Path]
        Path to the file with the Aztec code.

    Attributes
    ----------
    matrix : numpy.ndarray, shape (N, N)
        Lazy property - the binary module matrix (0 = white, 1 = black).

    Raises
    ------
    InvalidParameterError
        * The image file does not exist or cannot be read
        * Estimated cell size is zero (image too small or blurred)
        * Sampling point falls outside the image (wrong crop or resolution)
    UnsupportedSymbolError
        Computed side length *N* is even or outside the range 15 - 151.
    """

    def __init__(
        self, image_path: Union[str, Path], *, multiple: Optional[bool] = False
    ) -> None:
        self.image_path = Path(image_path)
        self._multiple = multiple
        if not self.image_path.exists():
            raise InvalidParameterError(f"file not found: {self.image_path}")
        if not self.image_path.is_file():
            raise InvalidParameterError(f"path is not a file: {self.image_path}")

    def _detect_rois(
        self,
        min_area_ratio: float = 0.005,
        ar_tol: float = 0.15,
        density_tol: float = 0.15,
    ) -> List[Tuple[np.ndarray, Tuple[int, int, int, int]]]:
        """Detect all candidate Aztec codes in the image and return the crops.

        Parameters
        ----------
        min_area_ratio : float, default 0.005
            Minimum area of the detected region as a fraction of the image area.

        ar_tol : float, default 0.15
            Allowed aspect ratio tolerance (width/height) for the detected region.

        density_tol : float, default 0.15
            Allowed density tolerance for the detected region (black/white ratio).

        Returns
        -------
        List[Tuple[crop_BGR, (x, y, w, h)]]
            One entry per code candidate.
        """

        img = cv2.imread(self.image_path)
        h, w = img.shape[:2]

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)

        # White background, black foreground
        _, bin_bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # 8-neighbors on "black code" => invert to make the code white (255) for detection
        inv = cv2.bitwise_not(bin_bw)
        n_labels, _, stats, _ = cv2.connectedComponentsWithStats(inv, connectivity=8)

        img_area = h * w
        rois = []  # results

        for i in range(1, n_labels):  # 0 = background, we start from 1
            x, y, ww, hh, area = stats[i]

            if area < img_area * min_area_ratio:
                continue

            ar = ww / float(hh)
            if not (1 - ar_tol <= ar <= 1 + ar_tol):
                continue

            # density : 50% black / 50% white
            roi_bin = bin_bw[y : y + hh, x : x + ww]
            black_ratio = 1 - cv2.countNonZero(roi_bin) / float(ww * hh)
            if abs(black_ratio - 0.5) > density_tol:
                continue

            crop = img[y : y + hh, x : x + ww].copy()
            rois.append((crop, (x, y, ww, hh)))

        for i, roi in enumerate(rois):
            cv2.imwrite(f"{i}.png", roi[0])

        print(len(rois))
        return rois

    def _estimate_N(self, binary: np.ndarray) -> int:
        h, w = binary.shape
        row = (binary[h // 2, :] < 128).astype(int)

        runs = []
        current = row[0]
        length = 1
        for pix in row[1:]:
            if pix == current:
                length += 1
            else:
                runs.append(length)
                length = 1
                current = pix
        runs.append(length)

        cell_size = int(np.median(runs))
        if cell_size == 0:
            raise InvalidParameterError(
                "estimated cell size is zero - image too small / blurred"
            )
        N = int(round(w / cell_size))
        if N % 2 == 0 or not (15 <= N <= 151):
            raise UnsupportedSymbolError(f"unsupported Aztec side length: {N}")
        return N

    def _matrix_from_crop(self, crop: np.ndarray) -> np.ndarray:
        """Convert a *single* square crop to a binary module matrix."""
        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        N = self._estimate_N(binary)
        h = binary.shape[0]
        cell_size = h // N
        if cell_size == 0:
            raise InvalidParameterError(
                "cell size computed as zero – check image resolution"
            )

        matrix = np.zeros((N, N), dtype=int)
        for y in range(N):
            for x in range(N):
                cx = int((x + 0.5) * cell_size)
                cy = int((y + 0.5) * cell_size)
                if cy >= h or cx >= binary.shape[1]:
                    raise InvalidParameterError(
                        "sampling point outside image – wrong crop or skewed image"
                    )
                matrix[y, x] = 1 if binary[cy, cx] < 128 else 0
        return matrix

    def _extract_matrix(self) -> List[np.ndarray]:
        rois = self._detect_rois() if self._multiple else []
        if not rois:  # No Aztec code croped, try to read the whole image
            img = cv2.imread(str(self.image_path))
            if img is None:
                raise InvalidParameterError(f"cannot read image: {self.image_path}")
            try:
                return [self._matrix_from_crop(img)]
            except (InvalidParameterError, UnsupportedSymbolError):
                return []  # no Aztec code found

        matrices = []
        for crop, _ in rois:
            try:
                matrices.append(self._matrix_from_crop(crop))
            except (InvalidParameterError, UnsupportedSymbolError) as e:
                # If exception is raised, pass to the next crop
                print(e)
                continue
        return matrices

    @cached_property
    def matrices(self) -> List[np.ndarray]:
        """List of module matrices detected in the image."""
        matrices = self._extract_matrix()
        if not matrices:
            raise InvalidParameterError("no Aztec matrix detected in the image")
        return matrices

    @cached_property
    def matrix(self) -> np.ndarray:
        """Return the first matrix detected in the image."""
        if not self.matrices:
            raise InvalidParameterError("no Aztec matrix detected in the image")
        return self.matrices[0]
