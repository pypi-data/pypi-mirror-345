# slack_blockkit_builder/builder.py

class BlockKitBuilder:
    @staticmethod
    def section(text, accessory=None):
        block = {
            "type": "section",
            "text": {"type": "mrkdwn", "text": text}
        }
        if accessory:
            block["accessory"] = accessory
        return block

    @staticmethod
    def button(text, action_id, style=None):
        button = {
            "type": "button",
            "text": {"type": "plain_text", "text": text},
            "action_id": action_id
        }
        if style:
            button["style"] = style
        return button

    @staticmethod
    def input(block_id, label, action_id, multiline=False):
        return {
            "type": "input",
            "block_id": block_id,
            "label": {"type": "plain_text", "text": label},
            "element": {
                "type": "plain_text_input",
                "action_id": action_id,
                "multiline": multiline
            }
        }

    @staticmethod
    def divider():
        return {"type": "divider"}

    @staticmethod
    def context(elements):
        return {"type": "context", "elements": elements}

    @staticmethod
    def plain_text(text):
        return {"type": "plain_text", "text": text}

    @staticmethod
    def markdown_text(text):
        return {"type": "mrkdwn", "text": text}
