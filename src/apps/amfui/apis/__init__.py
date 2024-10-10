from ninja import Router


from .alarmi.apis import router as alarmi_router

from .live_state.apis import router as live_state_router

from .live_state_manage.apis import router as live_state_manage_router

from .pezzi.apis import router as pezzi_router

from .stato.apis import router as stato_router

from .cell.apis import router as cell_router

from .record.apis import router as record_router

from .record_manage.apis import router as record_manage_router

from .work_sheet.apis import router as work_sheet_router

from .order.apis import router as order_router


router = Router(tags=['amfui'])


router.add_router('alarmi', alarmi_router)

router.add_router('live_state', live_state_router)

router.add_router('live_state_manage', live_state_manage_router)

router.add_router('pezzi', pezzi_router)

router.add_router('stato', stato_router)

router.add_router('cell', cell_router)

router.add_router('record', record_router)

router.add_router('record_manage', record_manage_router)

router.add_router('work_sheet', work_sheet_router)

router.add_router('order', order_router)
