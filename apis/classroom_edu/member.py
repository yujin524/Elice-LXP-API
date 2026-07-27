"""클래스룸 구성원(member) 조회·제거·등록 요청을 만드는 page 객체."""

from config import settings


class MemberPage:
    def __init__(self, api_client):
        self.api_client = api_client

    def get_member_list(
        self,
        *,
        classroom_id: str,
        filter_roles: str = "student",
        offset: int = 0,
        count: int = 50,
        skip: int = 0,
    ):
        """구성원 목록 조회 (CH_034 Step3). API가 offset과 별개로 skip도 필수로 요구한다."""
        return self.api_client.get(
            settings.API_BASE_URL,
            "/member",
            params={
                "classroom_id": classroom_id,
                "filter_roles": filter_roles,
                "offset": offset,
                "count": count,
                "skip": skip,
            },
        )

    def remove_member(self, *, member_id: str, classroom_id: str):
        """구성원 제거 (CH_034 Step1)."""
        return self.api_client.delete(
            settings.API_BASE_URL,
            f"/member/{member_id}",
            json={"classroom_id": classroom_id},
        )

    def add_members_bulk(self, *, classroom_id: str, account_ids: list[int], role: str = "student"):
        """구성원 일괄 등록 (CH_034 Step2). 비동기 처리라 task_id만 반환한다."""
        return self.api_client.post(
            settings.API_BASE_URL,
            "/member/bulk",
            json={"classroom_id": classroom_id, "account_ids": account_ids, "role": role},
        )
