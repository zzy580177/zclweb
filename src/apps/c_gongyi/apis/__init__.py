from ninja import Router


from .material_parm.apis import router as material_parm_router

from .step.apis import router as step_router

from .process.apis import router as process_router

from .craft.apis import router as craft_router

from .route.apis import router as route_router

from .virtual_process_route.apis import router as virtual_process_route_router


router = Router(tags=['c_gongyi'])


router.add_router('material_parm', material_parm_router)

router.add_router('step', step_router)

router.add_router('process', process_router)

router.add_router('craft', craft_router)

router.add_router('route', route_router)

router.add_router('virtual_process_route', virtual_process_route_router)
