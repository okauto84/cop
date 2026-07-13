# -*- coding: utf-8 -*-
"""
modelyl_manual 데이터 처리 파이프라인.

1. data/img 이미지 -> 텍스트 추출 -> data/txt 저장
2. data/txt -> BGE-m3-ko 임베딩 -> data/vec pickle 저장
"""

from __future__ import annotations

import argparse
import pickle
import re
from pathlib import Path
from typing import Any

import fitz
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DEFAULT_PDF_PATH = DATA_DIR / "modelyl_manual.pdf"
DEFAULT_IMG_DIR = DATA_DIR / "img"
DEFAULT_TXT_DIR = DATA_DIR / "txt"
DEFAULT_VEC_DIR = DATA_DIR / "vec"
DEFAULT_VEC_PICKLE = DEFAULT_VEC_DIR / "vectors_manual.p"
DEFAULT_DPI = 300
DEFAULT_IMAGE_FORMAT = "png"
DEFAULT_EMBED_MODEL = "dragonkue/BGE-m3-ko"

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}
PAGE_NAME_PATTERN = re.compile(r"page_(\d+)", re.IGNORECASE)


def _normalize_text(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n").strip()


def _page_number_from_image(path: Path) -> int | None:
    match = PAGE_NAME_PATTERN.search(path.stem)
    return int(match.group(1)) if match else None


def _list_image_files(image_dir: Path) -> list[Path]:
    if not image_dir.is_dir():
        raise NotADirectoryError(f"이미지 폴더를 찾을 수 없습니다: {image_dir}")
    return sorted(
        p for p in image_dir.iterdir()
        if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
    )


def _extract_text_from_pdf_page(pdf_path: Path, page_number: int) -> str:
    with fitz.open(pdf_path) as doc:
        if page_number < 1 or page_number > doc.page_count:
            return ""
        return _normalize_text(doc[page_number - 1].get_text("text"))


def _extract_text_with_ocr(image_path: Path) -> str:
    try:
        import easyocr
    except ImportError as e:
        raise ImportError(
            "OCR 폴백을 위해 easyocr가 필요합니다. 다음을 설치하세요:\n"
            "pip install easyocr"
        ) from e

    reader = easyocr.Reader(["ko", "en"], gpu=False, verbose=False)
    lines = reader.readtext(str(image_path), detail=0, paragraph=True)
    return _normalize_text("\n".join(lines))


def extract_text_from_image(
    image_path: Path,
    *,
    pdf_path: Path | None = DEFAULT_PDF_PATH,
    use_ocr_fallback: bool = True,
) -> str:
    """
    이미지 파일을 열어 검증한 뒤, 대응 PDF 페이지 텍스트를 우선 추출합니다.
    PDF 텍스트가 없으면 OCR로 폴백합니다.
    """
    with Image.open(image_path) as img:
        img.load()

    page_number = _page_number_from_image(image_path)
    if page_number is not None and pdf_path and pdf_path.is_file():
        pdf_text = _extract_text_from_pdf_page(pdf_path, page_number)
        if pdf_text:
            return pdf_text

    if use_ocr_fallback:
        return _extract_text_with_ocr(image_path)

    return ""


def images_to_text_files(
    image_dir: Path = DEFAULT_IMG_DIR,
    output_dir: Path = DEFAULT_TXT_DIR,
    *,
    pdf_path: Path = DEFAULT_PDF_PATH,
    overwrite: bool = False,
) -> list[Path]:
    """data/img의 모든 이미지를 읽어 동일 파일명(.txt)으로 data/txt에 저장합니다."""
    output_dir.mkdir(parents=True, exist_ok=True)
    image_files = _list_image_files(image_dir)
    if not image_files:
        raise FileNotFoundError(f"이미지 파일이 없습니다: {image_dir}")

    saved_paths: list[Path] = []
    for index, image_path in enumerate(image_files, start=1):
        txt_path = output_dir / f"{image_path.stem}.txt"
        if txt_path.exists() and not overwrite:
            saved_paths.append(txt_path)
            continue

        text = extract_text_from_image(image_path, pdf_path=pdf_path)
        txt_path.write_text(text, encoding="utf-8")
        saved_paths.append(txt_path)

        if index % 20 == 0 or index == len(image_files):
            print(f"  텍스트 추출 진행: {index}/{len(image_files)} ({image_path.name})")

    return saved_paths


def _read_text_with_fallback_encodings(path: Path) -> str:
    for encoding in ("utf-8", "utf-8-sig", "cp949", "euc-kr"):
        try:
            return _normalize_text(path.read_text(encoding=encoding))
        except UnicodeDecodeError:
            continue
    return _normalize_text(path.read_text(encoding="utf-8", errors="replace"))


def load_txt_items(txt_dir: Path = DEFAULT_TXT_DIR) -> list[dict[str, Any]]:
    """data/txt의 모든 .txt 파일을 JSON 직렬화 가능한 dict 리스트로 읽습니다."""
    if not txt_dir.is_dir():
        raise NotADirectoryError(f"텍스트 폴더를 찾을 수 없습니다: {txt_dir}")

    items: list[dict[str, Any]] = []
    for txt_path in sorted(txt_dir.glob("page_*.txt"), key=lambda p: p.name):
        items.append(
            {
                "filename": txt_path.name,
                "title": txt_path.stem,
                "text": _read_text_with_fallback_encodings(txt_path),
            }
        )
    return items


def embed_texts_with_bge_m3_ko(
    texts: list[str],
    model_name: str = DEFAULT_EMBED_MODEL,
    *,
    batch_size: int = 16,
    max_length: int = 1024,
    normalize_embeddings: bool = True,
    device: str | None = None,
) -> list[list[float]]:
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as e:
        raise ImportError(
            "임베딩을 위해 패키지가 필요합니다. 다음을 설치하세요:\n"
            "pip install -U sentence-transformers torch"
        ) from e

    if device is None:
        try:
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
        except (ImportError, OSError):
            device = "cpu"

    model = SentenceTransformer(model_name, trust_remote_code=True, device=device)
    model.max_seq_length = max_length
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=True,
        normalize_embeddings=normalize_embeddings,
    )
    return [vector.tolist() for vector in embeddings]


def add_embeddings_to_items(
    items: list[dict[str, Any]],
    *,
    text_key: str = "text",
    embed_key: str = "embedd",
    model_name: str = DEFAULT_EMBED_MODEL,
    batch_size: int = 16,
    max_length: int = 1024,
    normalize_embeddings: bool = True,
    device: str | None = None,
) -> list[dict[str, Any]]:
    texts = [str(item.get(text_key) or "") for item in items]
    embeddings = embed_texts_with_bge_m3_ko(
        texts,
        model_name=model_name,
        batch_size=batch_size,
        max_length=max_length,
        normalize_embeddings=normalize_embeddings,
        device=device,
    )

    embedded_items: list[dict[str, Any]] = []
    for item, embedding in zip(items, embeddings, strict=True):
        new_item = dict(item)
        new_item[embed_key] = embedding
        embedded_items.append(new_item)
    return embedded_items


def texts_to_vector_pickle(
    txt_dir: Path = DEFAULT_TXT_DIR,
    output_path: Path = DEFAULT_VEC_PICKLE,
    *,
    model_name: str = DEFAULT_EMBED_MODEL,
    batch_size: int = 16,
    max_length: int = 1024,
) -> Path:
    """data/txt 파일들을 읽어 임베딩 후 하나의 pickle 파일로 저장합니다."""
    items = load_txt_items(txt_dir)
    if not items:
        raise FileNotFoundError(f"텍스트 파일이 없습니다: {txt_dir}")

    embedded_items = add_embeddings_to_items(
        items,
        model_name=model_name,
        batch_size=batch_size,
        max_length=max_length,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as file:
        pickle.dump(embedded_items, file)

    return output_path


def pdf_to_images(
    pdf_path: Path,
    output_dir: Path,
    *,
    dpi: int = DEFAULT_DPI,
    image_format: str = DEFAULT_IMAGE_FORMAT,
) -> list[Path]:
    """PDF 각 페이지를 고해상도 이미지 파일로 저장합니다."""
    if not pdf_path.is_file():
        raise FileNotFoundError(f"PDF 파일을 찾을 수 없습니다: {pdf_path}")

    output_dir.mkdir(parents=True, exist_ok=True)
    image_format = image_format.lower().lstrip(".")
    zoom = dpi / 72.0
    matrix = fitz.Matrix(zoom, zoom)

    saved_paths: list[Path] = []
    with fitz.open(pdf_path) as doc:
        page_count = doc.page_count
        pad = max(3, len(str(page_count)))

        for page_index in range(page_count):
            page = doc.load_page(page_index)
            pixmap = page.get_pixmap(matrix=matrix, alpha=False)
            output_path = output_dir / f"page_{page_index + 1:0{pad}d}.{image_format}"
            if image_format in {"jpg", "jpeg"}:
                pixmap.save(output_path, output="jpeg", jpg_quality=95)
            else:
                pixmap.save(output_path)
            saved_paths.append(output_path)

    return saved_paths


def run_full_pipeline(
    *,
    image_dir: Path = DEFAULT_IMG_DIR,
    txt_dir: Path = DEFAULT_TXT_DIR,
    vec_path: Path = DEFAULT_VEC_PICKLE,
    pdf_path: Path = DEFAULT_PDF_PATH,
    overwrite_txt: bool = False,
    model_name: str = DEFAULT_EMBED_MODEL,
) -> None:
    print("[1/2] 이미지 -> 텍스트 추출")
    txt_paths = images_to_text_files(
        image_dir,
        txt_dir,
        pdf_path=pdf_path,
        overwrite=overwrite_txt,
    )
    print(f"  완료: {len(txt_paths)}개 -> {txt_dir}")

    print("[2/2] 텍스트 -> 임베딩 pickle 저장")
    saved_vec = texts_to_vector_pickle(
        txt_dir,
        vec_path,
        model_name=model_name,
    )
    print(f"  완료: {saved_vec}")


def main() -> None:
    parser = argparse.ArgumentParser(description="modelyl_manual 데이터 처리 파이프라인")
    subparsers = parser.add_subparsers(dest="command")

    pdf_parser = subparsers.add_parser("pdf-to-img", help="PDF를 페이지별 이미지로 변환")
    pdf_parser.add_argument("--pdf", type=Path, default=DEFAULT_PDF_PATH)
    pdf_parser.add_argument("--output-dir", type=Path, default=DEFAULT_IMG_DIR)
    pdf_parser.add_argument("--dpi", type=int, default=DEFAULT_DPI)

    img_parser = subparsers.add_parser("img-to-txt", help="이미지에서 텍스트 추출")
    img_parser.add_argument("--image-dir", type=Path, default=DEFAULT_IMG_DIR)
    img_parser.add_argument("--output-dir", type=Path, default=DEFAULT_TXT_DIR)
    img_parser.add_argument("--pdf", type=Path, default=DEFAULT_PDF_PATH)
    img_parser.add_argument("--overwrite", action="store_true")

    vec_parser = subparsers.add_parser("txt-to-vec", help="텍스트 임베딩 후 pickle 저장")
    vec_parser.add_argument("--txt-dir", type=Path, default=DEFAULT_TXT_DIR)
    vec_parser.add_argument("--output", type=Path, default=DEFAULT_VEC_PICKLE)
    vec_parser.add_argument("--model", default=DEFAULT_EMBED_MODEL)

    subparsers.add_parser("all", help="img-to-txt + txt-to-vec 순차 실행")

    args = parser.parse_args()
    command = args.command or "all"

    if command == "pdf-to-img":
        saved = pdf_to_images(args.pdf, args.output_dir, dpi=args.dpi)
        print(f"완료: {len(saved)}개 페이지 -> {args.output_dir}")
    elif command == "img-to-txt":
        saved = images_to_text_files(
            args.image_dir,
            args.output_dir,
            pdf_path=args.pdf,
            overwrite=args.overwrite,
        )
        print(f"완료: {len(saved)}개 -> {args.output_dir}")
    elif command == "txt-to-vec":
        saved = texts_to_vector_pickle(args.txt_dir, args.output, model_name=args.model)
        print(f"완료: {saved}")
    elif command == "all":
        run_full_pipeline(overwrite_txt=False)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
