import webview

from backend.events.eventTransferObjects import StepStatus, StepLogUpdate


class BackendEventApi:


    def sendStepLogs(self, stepLogs: StepLogUpdate):
        self.sendEvent("stepLogUpdate", stepLogs.to_json())

    def sendStepStatus(self, status: StepStatus):
        self.sendEvent("stepStatusUpdate", status.to_json())

    def sendEvent(self, event_name, data_json):
        if not webview.windows[0]:
            raise RuntimeError("No window set.")

        webview.windows[0].evaluate_js(f"""
                    (function() {{
                        const event = new CustomEvent('{event_name}', {{ detail: {data_json} }});
                        window.dispatchEvent(event);
                    }})();
                """)



