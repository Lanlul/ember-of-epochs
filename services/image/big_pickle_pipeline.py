import io
import logging
from pathlib import Path
from typing import Optional

from ...config import settings
from .style_controller import StyleController
from .guidance_scheduler import GuidanceScheduler
from .image_cache import ImageCache

logger = logging.getLogger(__name__)


class BigPicklePipeline:
    def __init__(
        self,
        style_controller: StyleController,
        guidance_scheduler: GuidanceScheduler,
        image_cache: ImageCache,
    ):
        self._style_controller = style_controller
        self._guidance_scheduler = guidance_scheduler
        self._image_cache = image_cache
        self._pipe = None
        self._device = settings.bigpickle_device

    async def initialize(self) -> None:
        if self._pipe is not None:
            return
        try:
            import torch
            from diffusers import DiffusionPipeline

            model_path = Path(settings.bigpickle_model_path)
            if not model_path.exists():
                logger.warning(
                    "Model not found at %s. Use mock mode.",
                    model_path,
                )
                self._pipe = None
                return

            use_fp16 = self._device == "cuda"
            pipe = DiffusionPipeline.from_pretrained(
                str(model_path),
                torch_dtype=torch.float16 if use_fp16 else torch.float32,
                variant="fp16" if use_fp16 else None,
            )
            pipe.to(self._device)
            torch.cuda.empty_cache()
            self._pipe = pipe
            logger.info("Image pipeline loaded successfully from %s", model_path)

        except ImportError as e:
            logger.warning(
                "diffusers/torch not installed: %s. Run: pip install diffusers torch", e
            )
            self._pipe = None
        except Exception as e:
            logger.error("Failed to initialize image pipeline: %s", e)
            self._pipe = None

    async def generate(
        self,
        prompt: str,
        negative_prompt: str,
        style: str,
        chapter: int = 1,
        is_key_moment: bool = False,
        output_path: Optional[str] = None,
    ) -> Optional[str]:
        cfg = self._guidance_scheduler.schedule(chapter, is_key_moment)

        if self._pipe is None:
            return await self._mock_generate(
                prompt, output_path
            )

        images = self._pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=settings.bigpickle_inference_steps,
            guidance_scale=cfg,
            height=512,
            width=512,
            num_images_per_prompt=1,
        ).images

        if not images:
            return None

        out = Path(output_path) if output_path else None
        if out:
            out.parent.mkdir(parents=True, exist_ok=True)
            images[0].save(out)
            return str(out)

        buf = io.BytesIO()
        images[0].save(buf, format="PNG")
        return buf.getvalue()

    async def _mock_generate(
        self,
        prompt: str,
        output_path: Optional[str] = None,
    ) -> Optional[str]:
        logger.warning("Mock generate (no model loaded): %s", prompt[:60])
        out = Path(output_path) if output_path else None
        if out:
            out.parent.mkdir(parents=True, exist_ok=True)
            self._create_placeholder(out)
            return str(out)
        return None

    def _create_placeholder(self, path: Path) -> None:
        try:
            from PIL import Image, ImageDraw, ImageFont

            img = Image.new("RGB", (768, 512), color=(20, 18, 30))
            draw = ImageDraw.Draw(img)
            try:
                font = ImageFont.truetype(
                    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc", 32
                )
            except Exception:
                font = ImageFont.load_default()
            text1 = "幻境編年史"
            bbox = draw.textbbox((0, 0), text1, font=font)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            draw.text(
                ((768 - tw) // 2, (512 - th) // 2 - 20),
                text1, fill=(230, 184, 92), font=font,
            )
            draw.text(
                ((768 - tw) // 2, (512 - th) // 2 + 30),
                "紀元餘燼", fill=(217, 74, 42), font=font,
            )
            img.save(path)
        except ImportError:
            pass
