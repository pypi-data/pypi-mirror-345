import os
import random
from pathlib import Path
import pytest
from PIL import Image
from genpattern import GPImgAlpha, gp_genpattern, GPExponentialSchedule

SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))

@pytest.fixture(autouse=True)
def setup_env() -> None:
    random.seed(42)

def load_and_modify_image(filepath: str,
                          copies: int = 1,
                          min_scale: float = 1.0,
                          max_scale: float = 2.0,
                          max_rotation: int = 360) -> list[tuple[GPImgAlpha, Image.Image]]:
    with Image.open(filepath) as img:
        if img.mode not in ("RGBA", "LA"):
            raise ValueError(f"The image at '{filepath}' doesn't have an alpha channel.")
        results = []
        for _ in range(copies):
            scale_factor = random.uniform(min_scale, max_scale)
            rotation_angle = random.randint(0, max_rotation)
            scaled_img = img.resize(
                (int(img.width * scale_factor), int(img.height * scale_factor)),
                resample=Image.Resampling.NEAREST
            )
            rotated_img = scaled_img.rotate(
                rotation_angle,
                expand=True,
                resample=Image.Resampling.NEAREST
            )
            alpha_data = rotated_img.split()[3] if rotated_img.mode == "RGBA" else rotated_img.split()[1]
            data = alpha_data.tobytes()
            img_alpha = GPImgAlpha(rotated_img.width, rotated_img.height, data)
            results.append((img_alpha, rotated_img))
    return results

def test_full_pipeline(tmp_path: Path) -> None:
    images = [os.path.join(SCRIPT_PATH, "test", x) for x in ["b1.png", "b2.png", "b3.png", "b4.png"]]
    WIDTH = 512
    HEIGHT = 512
    COPIES = 100
    collections_raw = [load_and_modify_image(path, copies=COPIES) for path in images]
    alphas = [[item[0] for item in coll] for coll in collections_raw]

    result = gp_genpattern(
        alphas,
        WIDTH,
        HEIGHT,
        threshold=64,
        offset_radius=5,
        collection_offset_radius=20,
        schedule=GPExponentialSchedule(0.8),
        seed=42
    )

    total_placements = sum(
        len(coords)
        for coll in result
        for coords in coll
    )
    assert total_placements > 0, "Expected at least one image placement, but none were placed."

    canvas = Image.new("RGBA", (WIDTH, HEIGHT), (255, 255, 255, 255))
    for coll_idx, coll in enumerate(result):
        for idx, coords in enumerate(coll):
            rotated_img = collections_raw[coll_idx][idx][1]
            for coord in coords:
                canvas.paste(rotated_img, coord, mask=rotated_img)

    output_file = tmp_path / "test.png"
    canvas.save(str(output_file))
    assert output_file.is_file()

