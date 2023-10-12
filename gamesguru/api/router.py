from ninja import Router


router = Router()


@router.get("/healthz")
def healthz(request):
    return {"message": "ok"}


@router.get("/add")
def add(request, a: int, b: int):
    return {
        "result": a + b
    }
