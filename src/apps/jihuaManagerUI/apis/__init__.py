from ninja import Router


from .p_order.apis import router as p_order_router

from .out_bound_manag.apis import router as out_bound_manag_router


router = Router(tags=['jihuaManagerUI'])


router.add_router('order', p_order_router)

router.add_router('out_bound_manag', out_bound_manag_router)
