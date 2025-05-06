from shein_api.api.base import BaseAPI
from shein_api.base.api_response import ApiResponse
from shein_api.base.helpers import action


class Feed(BaseAPI):

    @action("/open-api/sem/feed/createFeedDocument")
    def create_feed_document(self, content_type, **kwargs) -> ApiResponse:
        """
        创建Feed文件
        :param str content_type:
        :return:
        """
        data = {
            "contentType": content_type,
        }
        return self._request(data={**kwargs, **data})

    @action("/open-api/sem/feed/getFeedDocument", method="GET")
    def get_feed_document(self, feed_document_id, **kwargs) -> ApiResponse:
        """
        创建Feed文件
        :param str feed_document_id: feedDocumentId；示例：/open-api/sem/feed/getFeedDocument?feedDocumentId=MzgxMDk0NDVfMTBfNDI0XzE3MzM1NDQxMzkyMTY=.json
        :return:
        """
        params = {
            "feedDocumentId": feed_document_id,
        }
        return self._request(params={**kwargs, **params})

    @action("/open-api/sem/feed/uploadDocumentContent")
    def upload_document_content(self, feed_document_id, **kwargs) -> ApiResponse:
        """
        创建Feed文件
        :param str feed_document_id: feedDocumentId;示例：/open-api/sem/feed/uploadDocumentContent?feed_document_id=openapi-sem/2024-10-25/21613915_10_359_17298584717301157959690244.json
        :return:
        """
        data = {
            "feedDocumentId": feed_document_id,
        }
        return self._request(data={**kwargs, **data})

    @action("/open-api/sem/feed/createFeed")
    def create_feed(self, feed_document_id, feed_type, version, **kwargs) -> ApiResponse:
        """
        创建Feed文件
        :param (str, opt) feed_document_id: Feed文件的名称
        :param (str, opt) feed_type: 文件的处理方式，目前支持"PRODUCT_LISTING"
        :param (str, opt) version: 版本；默认无传
        :return:
        """
        data = {
            "feedDocumentId": feed_document_id,
            "feedType": feed_type,
            "version": version,
        }
        return self._request(data={**kwargs, **data})

    @action("/open-api/sem/feed/getFeed", method="GET")
    def get_feed(self, feed_id, **kwargs) -> ApiResponse:
        """
        查看Feed任务
        :param int feed_id: feedId;通过创建Feed任务获得
        :return:
        """
        params = {
            "feedId": feed_id,
        }
        return self._request(params={**kwargs, **params})

    @action("/open-api/sem/feed/cancelFeed")
    def cancel_feed(self, feed_id, **kwargs) -> ApiResponse:
        """
        取消Feed任务
        :param int feed_id: feedId;通过创建Feed任务获得
        :return:
        """
        data = {
            "feedId": feed_id,
        }
        return self._request(data={**kwargs, **data})
