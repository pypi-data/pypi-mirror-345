from fwdi.Domain.Configure.global_setting_service import GlobalSettingService


class ExtGlobalSetting():
    @staticmethod
    def parse_arg(**kwargs):
        config:GlobalSettingService = GlobalSettingService
        for key in kwargs:
            match key:
                case 'log_lvl':
                    config.log_lvl = kwargs.get('log_lvl', 0)
                case 'log_to_elastic':
                    config.log_to_elastic = kwargs.get('log_to_elastic', False)
                case 'elastic_log_conf':
                    config.elastic_log_conf = kwargs.get('elastic_log_conf', {})
                case 'log_to_file':
                    config.log_to_file = kwargs.get('log_to_file', False)
                case 'log_to_console':
                    config.log_to_console = kwargs.get('log_to_console', True)
                case 'file_log_conf':
                    config.file_log_conf = kwargs.get('file_log_conf', {})
                case 'log_split_by_name':
                    config.split_by_name = kwargs.get('log_split_by_name', False)
                case 'queue_name':
                    config.queue_name = kwargs.get('queue_name', '')
                case 'name':
                    config.name = kwargs.get('name', '')
                case 'description':
                    config.description = kwargs.get('description', '')
                case 'broker_conf':
                    config.broker_conf = kwargs.get('broker_conf', {})