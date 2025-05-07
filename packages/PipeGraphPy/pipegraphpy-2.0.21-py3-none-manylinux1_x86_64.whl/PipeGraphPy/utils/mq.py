# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# import traceback
# from PipeGraphPy.logger import log
# from PipeGraphPy.config import settings
# from PipeGraphPy.db.models import PredictRecordTB, MqTB
# from rabbitmqpy import Puber
# from datetime import datetime, timedelta
#
#
# def publish_predict_dict(predict_dict, **kwargs):
#     # global puber
#     puber = None
#     try:
#         if settings.RUN_PERMISSION:
#             try:
#                 if settings.DEBUG:
#                     puber = Puber(
#                         settings.AMQP_URL,
#                         'PipeGraphPypub_predict_e_test',
#                         'direct',
#                         routing_key='PipeGraphPypub_predict_k_test'
#                     )
#                 else:
#                     puber = Puber(
#                         settings.AMQP_URL,
#                         'PipeGraphPypub_predict_e',
#                         'direct',
#                         routing_key='PipeGraphPypub_predict_k'
#                     )
#             except:
#                 puber = None
#         else:
#             puber = None
#         if puber is not None:
#             puber.send(predict_dict)
#             log_info = '发送MQ：exchange=PipeGraphPypub_predict_e,routing_key=PipeGraphPypub_predict_k,body=%s' % (
#                 str(predict_dict)[:100]
#             )
#             MqTB.add(
#                 pubdate=int((datetime.utcnow()+timedelta(hours=8)).strftime("%Y%m%d")),
#                 graph_id=predict_dict.get("id", 0),
#                 exchange="PipeGraphPypub_predict_e",
#                 queue="",
#                 route_key="PipeGraphPypub_predict_k",
#                 clock=predict_dict.get("clock", "12"),
#                 kind = 1
#                 )
#             log.info(log_info, **kwargs)
#             if kwargs.get('plog_record_id'):
#                 PredictRecordTB.set(is_pub=1).where(id=kwargs['plog_record_id'])
#     except Exception:
#         log.error(traceback.format_exc(), **kwargs)
