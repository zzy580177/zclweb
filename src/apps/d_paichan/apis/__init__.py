from ninja import Router

from .production_plan.apis import router as production_plan_router
from .production_order.apis import router as production_order_router
from .work_order.apis import router as work_order_router

router = Router(tags=['d_paichan'])

router.add_router('production_plan', production_plan_router)
router.add_router('production_order', production_order_router)
router.add_router('work_order', work_order_router)
