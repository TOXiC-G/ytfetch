class Theme:
    DARK_QSS = """
    /* Main Window & Core */
    QMainWindow, QDialog, QWidget#CentralWidget {
        background-color: #0f1117;
        color: #f3f4f6;
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
        font-size: 13px;
    }

    QWidget {
        color: #f3f4f6;
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    }

    /* Cards and Surfaces */
    QFrame#Card, QFrame#PreviewCard, QFrame#OptionsCard {
        background-color: #171923;
        border: 1px solid #272a38;
        border-radius: 12px;
    }

    QFrame#Card:hover, QFrame#PreviewCard:hover {
        border-color: #3b3f52;
    }

    /* Queue Item Card */
    QFrame#QueueItemCard {
        background-color: #161822;
        border: 1px solid #262938;
        border-radius: 10px;
    }
    QFrame#QueueItemCard:hover {
        border-color: #383c50;
        background-color: #1a1c28;
    }

    /* Scroll Area fixes */
    QScrollArea {
        background-color: transparent;
        border: none;
    }
    QScrollArea > QWidget > QWidget {
        background-color: transparent;
    }

    /* Headers and Labels */
    QLabel {
        color: #f3f4f6;
    }
    QLabel#HeaderTitle {
        font-size: 19px;
        font-weight: 700;
        color: #ffffff;
        letter-spacing: -0.5px;
    }
    QLabel#SectionTitle {
        font-size: 14px;
        font-weight: 600;
        color: #e2e8f0;
    }
    QLabel#PreviewTitle {
        font-size: 15px;
        font-weight: 700;
        color: #ffffff;
    }
    QLabel#PreviewUploader {
        font-size: 13px;
        font-weight: 600;
        color: #cbd5e1;
    }
    QLabel#QueueItemTitle {
        font-size: 13px;
        font-weight: 600;
        color: #ffffff;
    }
    QLabel#MutedLabel {
        color: #94a3b8;
        font-size: 12px;
    }
    QLabel#Badge {
        background-color: #272a38;
        color: #38bdf8;
        border-radius: 6px;
        padding: 3px 8px;
        font-size: 11px;
        font-weight: 600;
    }
    QLabel#StatusSuccess {
        background-color: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 6px;
        padding: 3px 8px;
        font-size: 11px;
        font-weight: 600;
    }
    QLabel#StatusError {
        background-color: rgba(239, 68, 68, 0.15);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.3);
        border-radius: 6px;
        padding: 3px 8px;
        font-size: 11px;
        font-weight: 600;
    }

    /* Inputs */
    QLineEdit {
        background-color: #11131a;
        color: #f8fafc;
        border: 1.5px solid #272a38;
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 13px;
        selection-background-color: #e11d48;
    }
    QLineEdit:focus {
        border-color: #e11d48;
        background-color: #141722;
    }
    QLineEdit:hover {
        border-color: #373b4e;
    }

    /* ComboBox */
    QComboBox {
        background-color: #171923;
        color: #f8fafc;
        border: 1px solid #2d3142;
        border-radius: 8px;
        padding: 7px 12px;
        font-size: 12px;
        font-weight: 500;
    }
    QComboBox:hover {
        border-color: #4b5268;
        background-color: #1d2130;
    }
    QComboBox::drop-down {
        border: none;
        width: 24px;
    }
    QComboBox QAbstractItemView {
        background-color: #171923;
        color: #f8fafc;
        selection-background-color: #e11d48;
        selection-color: #ffffff;
        border: 1px solid #2d3142;
        border-radius: 8px;
        padding: 4px;
        outline: none;
    }

    /* Buttons */
    QPushButton {
        background-color: #212534;
        color: #f8fafc;
        border: 1px solid #2e3347;
        border-radius: 8px;
        padding: 8px 16px;
        font-size: 13px;
        font-weight: 600;
    }
    QPushButton:hover {
        background-color: #2a2f42;
        border-color: #424a64;
    }
    QPushButton:pressed {
        background-color: #181b26;
    }
    QPushButton:disabled {
        background-color: #141722;
        color: #64748b;
        border-color: #1e2230;
    }

    /* Primary Radiant Button */
    QPushButton#PrimaryButton {
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #e11d48, stop:1 #f43f5e);
        color: #ffffff;
        border: none;
        border-radius: 8px;
        font-weight: 700;
        padding: 9px 20px;
    }
    QPushButton#PrimaryButton:hover {
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #f43f5e, stop:1 #fb7185);
    }
    QPushButton#PrimaryButton:pressed {
        background-color: #be123c;
    }

    /* Secondary Accent Button */
    QPushButton#SecondaryAccentButton {
        background-color: #1e293b;
        color: #38bdf8;
        border: 1px solid #0284c7;
        border-radius: 8px;
        font-weight: 600;
        padding: 8px 16px;
    }
    QPushButton#SecondaryAccentButton:hover {
        background-color: #0369a1;
        color: #ffffff;
    }

    /* Update Available Glowing Button */
    QPushButton#UpdateNoticeButton {
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8b5cf6, stop:1 #a855f7);
        color: #ffffff;
        border: 1px solid #c084fc;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 700;
        padding: 4px 12px;
    }
    QPushButton#UpdateNoticeButton:hover {
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #9333ea, stop:1 #c084fc);
    }

    /* Action Pill Buttons (for Queue items) */
    QPushButton#QueueActionBtn {
        background-color: #212534;
        color: #e2e8f0;
        border: 1px solid #33384c;
        border-radius: 6px;
        padding: 3px 12px;
        font-size: 11px;
        font-weight: 600;
        min-height: 26px;
    }
    QPushButton#QueueActionBtn:hover {
        background-color: #2c3246;
        border-color: #49516d;
        color: #ffffff;
    }

    /* Table & Inline Action Buttons */
    QPushButton#TableActionBtnOpen {
        background-color: rgba(56, 189, 248, 0.12);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.3);
        border-radius: 6px;
        font-weight: 600;
        font-size: 11px;
        padding: 3px 10px;
        min-height: 24px;
        max-height: 26px;
    }
    QPushButton#TableActionBtnOpen:hover {
        background-color: rgba(56, 189, 248, 0.25);
        border-color: #38bdf8;
        color: #ffffff;
    }
    QPushButton#TableActionBtnOpen:disabled {
        background-color: rgba(100, 116, 139, 0.1);
        color: #64748b;
        border-color: rgba(100, 116, 139, 0.2);
    }

    QPushButton#TableActionBtnFolder {
        background-color: rgba(234, 179, 8, 0.12);
        color: #fbbf24;
        border: 1px solid rgba(234, 179, 8, 0.3);
        border-radius: 6px;
        font-weight: 600;
        font-size: 11px;
        padding: 3px 10px;
        min-height: 24px;
        max-height: 26px;
    }
    QPushButton#TableActionBtnFolder:hover {
        background-color: rgba(234, 179, 8, 0.25);
        border-color: #fbbf24;
        color: #ffffff;
    }
    QPushButton#TableActionBtnFolder:disabled {
        background-color: rgba(100, 116, 139, 0.1);
        color: #64748b;
        border-color: rgba(100, 116, 139, 0.2);
    }

    QPushButton#TableActionBtnDelete {
        background-color: rgba(239, 68, 68, 0.1);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.25);
        border-radius: 6px;
        font-weight: 600;
        font-size: 11px;
        padding: 3px 8px;
        min-height: 24px;
        max-height: 26px;
        min-width: 24px;
    }
    QPushButton#TableActionBtnDelete:hover {
        background-color: rgba(239, 68, 68, 0.25);
        border-color: #f87171;
        color: #ffffff;
    }

    QPushButton#IconButton {
        background-color: transparent;
        border: 1px solid transparent;
        border-radius: 6px;
        padding: 5px;
    }
    QPushButton#IconButton:hover {
        background-color: #272a38;
        border-color: #3b3f52;
    }

    /* Progress Bar */
    QProgressBar {
        background-color: #11131a;
        border: 1px solid #272a38;
        border-radius: 5px;
        height: 8px;
        text-align: center;
        color: transparent;
    }
    QProgressBar::chunk {
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #e11d48, stop:0.5 #ec4899, stop:1 #38bdf8);
        border-radius: 4px;
    }

    /* Tabs */
    QTabWidget::pane {
        border: 1px solid #272a38;
        border-radius: 10px;
        background-color: #13151e;
        top: -1px;
    }
    QTabBar::tab {
        background-color: #171923;
        color: #94a3b8;
        border: 1px solid #272a38;
        border-bottom: none;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        padding: 8px 20px;
        margin-right: 4px;
        font-weight: 600;
        font-size: 13px;
    }
    QTabBar::tab:selected {
        background-color: #13151e;
        color: #ffffff;
        border-color: #3b3f52;
        border-bottom: 2px solid #e11d48;
    }
    QTabBar::tab:hover:!selected {
        background-color: #1e2230;
        color: #e2e8f0;
    }

    /* CheckBoxes & RadioButtons */
    QCheckBox, QRadioButton {
        spacing: 8px;
        color: #cbd5e1;
        font-size: 12px;
        font-weight: 500;
    }
    QCheckBox::indicator, QRadioButton::indicator {
        width: 18px;
        height: 18px;
        border-radius: 4px;
        border: 1.5px solid #3b3f52;
        background-color: #11131a;
    }
    QRadioButton::indicator {
        border-radius: 9px;
    }
    QCheckBox::indicator:hover, QRadioButton::indicator:hover {
        border-color: #e11d48;
    }
    QCheckBox::indicator:checked, QRadioButton::indicator:checked {
        background-color: #e11d48;
        border-color: #e11d48;
    }

    /* Scrollbars (Lighter Handle, Dark Trough) */
    QScrollBar:vertical {
        background-color: #11131a;
        width: 10px;
        margin: 0px;
        border-radius: 5px;
    }
    QScrollBar::handle:vertical {
        background-color: #3b4255;
        min-height: 35px;
        border-radius: 4px;
        margin: 1px 1px 1px 1px;
    }
    QScrollBar::handle:vertical:hover {
        background-color: #555f7b;
    }
    QScrollBar::handle:vertical:pressed {
        background-color: #e11d48;
    }
    QScrollBar::sub-line:vertical, QScrollBar::add-line:vertical {
        height: 0px;
        width: 0px;
        background: transparent;
        border: none;
    }
    QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
        height: 0px;
        width: 0px;
        background: transparent;
    }
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
        background: transparent;
    }

    QScrollBar:horizontal {
        background-color: #11131a;
        height: 10px;
        margin: 0px;
        border-radius: 5px;
    }
    QScrollBar::handle:horizontal {
        background-color: #3b4255;
        min-width: 35px;
        border-radius: 4px;
        margin: 1px;
    }
    QScrollBar::handle:horizontal:hover {
        background-color: #555f7b;
    }
    QScrollBar::handle:horizontal:pressed {
        background-color: #e11d48;
    }
    QScrollBar::sub-line:horizontal, QScrollBar::add-line:horizontal {
        width: 0px;
        background: transparent;
    }
    QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
        background: transparent;
    }

    /* Tables */
    QTableWidget {
        background-color: #171923;
        border: 1px solid #272a38;
        border-radius: 8px;
        gridline-color: #202433;
        color: #f3f4f6;
        selection-background-color: #272e42;
        selection-color: #ffffff;
    }
    QHeaderView::section {
        background-color: #11131a;
        color: #94a3b8;
        padding: 8px;
        border: none;
        border-bottom: 1px solid #272a38;
        font-weight: 600;
        font-size: 12px;
    }

    /* Banner / Toast */
    QFrame#Banner {
        background-color: #1e1b2e;
        border: 1px solid #8b5cf6;
        border-radius: 8px;
        padding: 8px 12px;
    }
    """

    LIGHT_QSS = """
    /* Main Window & Core */
    QMainWindow, QDialog, QWidget#CentralWidget {
        background-color: #f8fafc;
        color: #0f172a;
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
        font-size: 13px;
    }

    QWidget {
        color: #0f172a;
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    }

    /* Cards and Surfaces */
    QFrame#Card, QFrame#PreviewCard, QFrame#OptionsCard {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
    }

    QFrame#Card:hover, QFrame#PreviewCard:hover {
        border-color: #cbd5e1;
    }

    /* Queue Item Card */
    QFrame#QueueItemCard {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
    }
    QFrame#QueueItemCard:hover {
        border-color: #cbd5e1;
        background-color: #fcfdfe;
    }

    /* Scroll Area fixes */
    QScrollArea {
        background-color: transparent;
        border: none;
    }
    QScrollArea > QWidget > QWidget {
        background-color: transparent;
    }

    /* Headers and Labels */
    QLabel {
        color: #0f172a;
    }
    QLabel#HeaderTitle {
        font-size: 19px;
        font-weight: 700;
        color: #0f172a;
        letter-spacing: -0.5px;
    }
    QLabel#SectionTitle {
        font-size: 14px;
        font-weight: 600;
        color: #1e293b;
    }
    QLabel#PreviewTitle {
        font-size: 15px;
        font-weight: 700;
        color: #0f172a;
    }
    QLabel#PreviewUploader {
        font-size: 13px;
        font-weight: 600;
        color: #475569;
    }
    QLabel#QueueItemTitle {
        font-size: 13px;
        font-weight: 600;
        color: #0f172a;
    }
    QLabel#MutedLabel {
        color: #64748b;
        font-size: 12px;
    }
    QLabel#Badge {
        background-color: #e0f2fe;
        color: #0284c7;
        border-radius: 6px;
        padding: 3px 8px;
        font-size: 11px;
        font-weight: 600;
    }
    QLabel#StatusSuccess {
        background-color: #dcfce7;
        color: #15803d;
        border: 1px solid #bbf7d0;
        border-radius: 6px;
        padding: 3px 8px;
        font-size: 11px;
        font-weight: 600;
    }
    QLabel#StatusError {
        background-color: #fee2e2;
        color: #b91c1c;
        border: 1px solid #fecaca;
        border-radius: 6px;
        padding: 3px 8px;
        font-size: 11px;
        font-weight: 600;
    }

    /* Inputs */
    QLineEdit {
        background-color: #ffffff;
        color: #0f172a;
        border: 1.5px solid #cbd5e1;
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 13px;
        selection-background-color: #e11d48;
    }
    QLineEdit:focus {
        border-color: #e11d48;
        background-color: #ffffff;
    }
    QLineEdit:hover {
        border-color: #94a3b8;
    }

    /* ComboBox */
    QComboBox {
        background-color: #ffffff;
        color: #0f172a;
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        padding: 7px 12px;
        font-size: 12px;
        font-weight: 500;
    }
    QComboBox:hover {
        border-color: #94a3b8;
        background-color: #f8fafc;
    }
    QComboBox::drop-down {
        border: none;
        width: 24px;
    }
    QComboBox QAbstractItemView {
        background-color: #ffffff;
        color: #0f172a;
        selection-background-color: #e11d48;
        selection-color: #ffffff;
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        padding: 4px;
        outline: none;
    }

    /* Buttons */
    QPushButton {
        background-color: #f1f5f9;
        color: #0f172a;
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        padding: 8px 16px;
        font-size: 13px;
        font-weight: 600;
    }
    QPushButton:hover {
        background-color: #e2e8f0;
        border-color: #94a3b8;
    }
    QPushButton:pressed {
        background-color: #cbd5e1;
    }
    QPushButton:disabled {
        background-color: #f8fafc;
        color: #94a3b8;
        border-color: #e2e8f0;
    }

    /* Primary Button */
    QPushButton#PrimaryButton {
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #e11d48, stop:1 #f43f5e);
        color: #ffffff;
        border: none;
        border-radius: 8px;
        font-weight: 700;
        padding: 9px 20px;
    }
    QPushButton#PrimaryButton:hover {
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #f43f5e, stop:1 #fb7185);
    }
    QPushButton#PrimaryButton:pressed {
        background-color: #be123c;
    }

    /* Secondary Accent Button */
    QPushButton#SecondaryAccentButton {
        background-color: #f0f9ff;
        color: #0284c7;
        border: 1px solid #38bdf8;
        border-radius: 8px;
        font-weight: 600;
        padding: 8px 16px;
    }
    QPushButton#SecondaryAccentButton:hover {
        background-color: #0284c7;
        color: #ffffff;
    }

    /* Update Notice Button */
    QPushButton#UpdateNoticeButton {
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7c3aed, stop:1 #8b5cf6);
        color: #ffffff;
        border: 1px solid #a78bfa;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 700;
        padding: 4px 12px;
    }
    QPushButton#UpdateNoticeButton:hover {
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6d28d9, stop:1 #7c3aed);
    }

    /* Action Pill Buttons (for Queue items) */
    QPushButton#QueueActionBtn {
        background-color: #f1f5f9;
        color: #334155;
        border: 1px solid #cbd5e1;
        border-radius: 6px;
        padding: 3px 12px;
        font-size: 11px;
        font-weight: 600;
        min-height: 26px;
    }
    QPushButton#QueueActionBtn:hover {
        background-color: #e2e8f0;
        border-color: #94a3b8;
        color: #0f172a;
    }

    /* Table & Inline Action Buttons */
    QPushButton#TableActionBtnOpen {
        background-color: #f0f9ff;
        color: #0284c7;
        border: 1px solid #bae6fd;
        border-radius: 6px;
        font-weight: 600;
        font-size: 11px;
        padding: 3px 10px;
        min-height: 24px;
        max-height: 26px;
    }
    QPushButton#TableActionBtnOpen:hover {
        background-color: #0284c7;
        border-color: #0284c7;
        color: #ffffff;
    }
    QPushButton#TableActionBtnOpen:disabled {
        background-color: #f8fafc;
        color: #94a3b8;
        border-color: #e2e8f0;
    }

    QPushButton#TableActionBtnFolder {
        background-color: #fefce8;
        color: #d97706;
        border: 1px solid #fde68a;
        border-radius: 6px;
        font-weight: 600;
        font-size: 11px;
        padding: 3px 10px;
        min-height: 24px;
        max-height: 26px;
    }
    QPushButton#TableActionBtnFolder:hover {
        background-color: #d97706;
        border-color: #d97706;
        color: #ffffff;
    }
    QPushButton#TableActionBtnFolder:disabled {
        background-color: #f8fafc;
        color: #94a3b8;
        border-color: #e2e8f0;
    }

    QPushButton#TableActionBtnDelete {
        background-color: #fef2f2;
        color: #dc2626;
        border: 1px solid #fecaca;
        border-radius: 6px;
        font-weight: 600;
        font-size: 11px;
        padding: 3px 8px;
        min-height: 24px;
        max-height: 26px;
        min-width: 24px;
    }
    QPushButton#TableActionBtnDelete:hover {
        background-color: #dc2626;
        border-color: #dc2626;
        color: #ffffff;
    }

    QPushButton#IconButton {
        background-color: transparent;
        border: 1px solid transparent;
        border-radius: 6px;
        padding: 5px;
    }
    QPushButton#IconButton:hover {
        background-color: #e2e8f0;
        border-color: #cbd5e1;
    }

    /* Progress Bar */
    QProgressBar {
        background-color: #e2e8f0;
        border: 1px solid #cbd5e1;
        border-radius: 5px;
        height: 8px;
        text-align: center;
        color: transparent;
    }
    QProgressBar::chunk {
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #e11d48, stop:0.5 #ec4899, stop:1 #0284c7);
        border-radius: 4px;
    }

    /* Tabs */
    QTabWidget::pane {
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        background-color: #ffffff;
        top: -1px;
    }
    QTabBar::tab {
        background-color: #f1f5f9;
        color: #64748b;
        border: 1px solid #e2e8f0;
        border-bottom: none;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        padding: 8px 20px;
        margin-right: 4px;
        font-weight: 600;
        font-size: 13px;
    }
    QTabBar::tab:selected {
        background-color: #ffffff;
        color: #0f172a;
        border-color: #cbd5e1;
        border-bottom: 2px solid #e11d48;
    }

    /* CheckBoxes & RadioButtons */
    QCheckBox, QRadioButton {
        spacing: 8px;
        color: #334155;
        font-size: 12px;
        font-weight: 500;
    }
    QCheckBox::indicator, QRadioButton::indicator {
        width: 18px;
        height: 18px;
        border-radius: 4px;
        border: 1.5px solid #cbd5e1;
        background-color: #ffffff;
    }
    QRadioButton::indicator {
        border-radius: 9px;
    }
    QCheckBox::indicator:hover, QRadioButton::indicator:hover {
        border-color: #e11d48;
    }
    QCheckBox::indicator:checked, QRadioButton::indicator:checked {
        background-color: #e11d48;
        border-color: #e11d48;
    }

    /* Scrollbars (Light Mode) */
    QScrollBar:vertical {
        background-color: #f1f5f9;
        width: 10px;
        margin: 0px;
        border-radius: 5px;
    }
    QScrollBar::handle:vertical {
        background-color: #cbd5e1;
        min-height: 35px;
        border-radius: 4px;
        margin: 1px;
    }
    QScrollBar::handle:vertical:hover {
        background-color: #94a3b8;
    }
    QScrollBar::handle:vertical:pressed {
        background-color: #64748b;
    }
    QScrollBar::sub-line:vertical, QScrollBar::add-line:vertical {
        height: 0px;
        width: 0px;
        background: transparent;
        border: none;
    }
    QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
        height: 0px;
        width: 0px;
        background: transparent;
    }
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
        background: transparent;
    }

    QScrollBar:horizontal {
        background-color: #f1f5f9;
        height: 10px;
        margin: 0px;
        border-radius: 5px;
    }
    QScrollBar::handle:horizontal {
        background-color: #cbd5e1;
        min-width: 35px;
        border-radius: 4px;
        margin: 1px;
    }
    QScrollBar::handle:horizontal:hover {
        background-color: #94a3b8;
    }
    QScrollBar::handle:horizontal:pressed {
        background-color: #64748b;
    }
    QScrollBar::sub-line:horizontal, QScrollBar::add-line:horizontal {
        width: 0px;
        background: transparent;
    }
    QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
        background: transparent;
    }

    /* Tables */
    QTableWidget {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        gridline-color: #f1f5f9;
        color: #0f172a;
        selection-background-color: #e0f2fe;
        selection-color: #0f172a;
    }
    QHeaderView::section {
        background-color: #f8fafc;
        color: #64748b;
        padding: 8px;
        border: none;
        border-bottom: 1px solid #e2e8f0;
        font-weight: 600;
        font-size: 12px;
    }

    /* Banner / Toast */
    QFrame#Banner {
        background-color: #f5f3ff;
        border: 1px solid #c4b5fd;
        border-radius: 8px;
        padding: 8px 12px;
    }
    """

    @classmethod
    def get_stylesheet(cls, theme_name: str) -> str:
        if theme_name.lower() == "light":
            return cls.LIGHT_QSS
        return cls.DARK_QSS
