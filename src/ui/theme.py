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
    QFrame#Card, QFrame#PreviewCard, QFrame#OptionsCard, QFrame#QueueItemCard {
        background-color: #171923;
        border: 1px solid #272a38;
        border-radius: 12px;
    }

    QFrame#Card:hover, QFrame#PreviewCard:hover {
        border-color: #3b3f52;
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

    /* Primary Accent Button */
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

    /* Secondary Accent Button (e.g. Add to queue) */
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

    /* Icon Buttons / Tiny Buttons */
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
        border-radius: 6px;
        height: 10px;
        text-align: center;
        color: transparent;
    }
    QProgressBar::chunk {
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #e11d48, stop:1 #38bdf8);
        border-radius: 5px;
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

    /* Scrollbars */
    QScrollBar:vertical {
        background: #0f1117;
        width: 10px;
        margin: 0px;
        border-radius: 5px;
    }
    QScrollBar::handle:vertical {
        background: #272a38;
        min-height: 25px;
        border-radius: 5px;
    }
    QScrollBar::handle:vertical:hover {
        background: #3b3f52;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
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
    QFrame#Card, QFrame#PreviewCard, QFrame#OptionsCard, QFrame#QueueItemCard {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
    }

    QFrame#Card:hover, QFrame#PreviewCard:hover {
        border-color: #cbd5e1;
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

    /* Primary Accent Button */
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

    /* Progress Bar */
    QProgressBar {
        background-color: #e2e8f0;
        border: 1px solid #cbd5e1;
        border-radius: 6px;
        height: 10px;
        text-align: center;
        color: transparent;
    }
    QProgressBar::chunk {
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #e11d48, stop:1 #0284c7);
        border-radius: 5px;
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
