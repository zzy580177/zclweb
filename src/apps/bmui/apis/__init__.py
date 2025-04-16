from ninja import Router


from .material.apis import router as material_router

from .bom.apis import router as bom_router

from .bom_level.apis import router as bom_level_router


router = Router(tags=['bmui'])


router.add_router('material', material_router)

router.add_router('bom', bom_router)

router.add_router('bom_level', bom_level_router)
