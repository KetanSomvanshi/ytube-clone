import unittest
from unittest.mock import MagicMock, patch
from unittest.mock import Mock

from data_adapter.redis import Cache
from data_adapter.ytube import YTubeVideoMeta
from integrations.google_api_integration import GoogleYoutubeIntegration
from logger import logger
from models.base import PaginationRequest, GenericResponseModel
from usecases.admin_usecase import AdminUseCase
from usecases.ytube_usecase import YTubeUseCase
from utils.utils import ApiLockManager


class TestYTubeUseCase(unittest.TestCase):
    @patch("usecases.ytube_usecase.YTubeVideoMeta.list_ytube_videos_meta")
    @patch("usecases.ytube_usecase.YTubeUseCase.get_total_data_count")
    def test_get_videos_metadata(self, mock_get_total_data_count, mock_list_ytube_videos_meta):
        mock_get_total_data_count.return_value = 10
        mock_list_ytube_videos_meta.return_value = [Mock(), Mock()]
        paginator = PaginationRequest(limit=2, offset=0)

        response = YTubeUseCase.get_videos_metadata(paginator)

        self.assertIsInstance(response, GenericResponseModel)
        self.assertEqual(response.data.data, [Mock(), Mock()])
        self.assertEqual(response.data.pagination_data.total_count, 10)
        self.assertEqual(response.message, YTubeUseCase.MSG_GET_VIDEOS_META_SUCCESS)


class YTubeUseCaseTestCase(unittest.TestCase):
    def setUp(self):
        # mocking redis cache
        self.cache = Cache.get_instance()
        self.cache.get = MagicMock(return_value=None)
        self.cache.set = MagicMock()
        self.cache.increment = MagicMock()

        # mocking YTubeVideoMeta model
        self.ytube_video_meta = YTubeVideoMeta()
        self.ytube_video_meta.insert_all = MagicMock()

        # mocking AdminUseCase
        self.admin_usecase = AdminUseCase()
        self.admin_usecase.get_random_api_key = MagicMock(return_value=GenericResponseModel(data="api_key"))

        # mocking GoogleYoutubeIntegration
        self.google_youtube_integration = GoogleYoutubeIntegration()
        self.google_youtube_integration.sync_videos_meta_from_youtube = MagicMock(
            return_value=GenericResponseModel(
                data={
                    "items": [
                        {
                            "snippet": {
                                "publishedAt": "2022-11-12T00:00:00.00Z"
                            }
                        },
                        {
                            "snippet": {
                                "publishedAt": "2022-11-14T00:00:00.00Z"
                            }
                        }
                    ]
                }
            )
        )

        # mocking logger
        self.logger = logger
        self.logger.info = MagicMock()
        self.logger.debug = MagicMock()
        self.logger.error = MagicMock()