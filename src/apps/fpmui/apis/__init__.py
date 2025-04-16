from ninja import Router


from .step.apis import router as step_router

from .process_step.apis import router as process_step_router

from .process_route.apis import router as process_route_router

from .virtual_process_route.apis import router as virtual_process_route_router


router = Router(tags=['fpmui'])


router.add_router('step', step_router)

router.add_router('process_step', process_step_router)

router.add_router('process_route', process_route_router)

router.add_router('virtual_process_route', virtual_process_route_router)
