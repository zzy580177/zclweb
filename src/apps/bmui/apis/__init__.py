from ninja import Router


from .attribute.apis import router as attribute_router

from .material_group.apis import router as material_group_router

from .material.apis import router as material_router

from .bom.apis import router as bom_router


router = Router(tags=['bmui'])


router.add_router('attribute', attribute_router)

router.add_router('material_group', material_group_router)

router.add_router('material', material_router)

router.add_router('bom', bom_router)
