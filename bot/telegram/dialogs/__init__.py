from .start import router
from .poll.dialog import poll_dialog

router.include_router(poll_dialog)