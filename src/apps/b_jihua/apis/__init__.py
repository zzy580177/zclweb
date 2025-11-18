from ninja import Router


from .order.apis import router as order_router

from .order_parts.apis import router as order_parts_router


router = Router(tags=['b_jihua'])


router.add_router('order', order_router)

router.add_router('order_parts', order_parts_router)
