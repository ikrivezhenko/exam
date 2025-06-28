import os
from io import BytesIO
from datetime import date
from flask import current_app
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH


def translate_date_to_ru(date: str) -> str:
    date = date.replace("May", "Мая").replace("June", "Июня").replace("July", "Июля").replace("August", "Августа")
    return date


def replace_placeholder(doc, placeholder, replacement):
    """Заменяет плейсхолдер во всех элементах документа"""
    # В параграфах
    for p in doc.paragraphs:
        if placeholder in p.text:
            for run in p.runs:
                if placeholder in run.text:
                    run.text = run.text.replace(placeholder, replacement)

    # В таблицах
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                if placeholder in cell.text:
                    for paragraph in cell.paragraphs:
                        for run in paragraph.runs:
                            if placeholder in run.text:
                                run.text = run.text.replace(placeholder, replacement)


def format_role(role):
    """Форматирует роль для отображения в документах с учетом разных вариантов написания"""
    role_lower = role.lower()
    if 'член' in role_lower or 'член' in role_lower:
        return 'член комиссии'
    elif 'зам' in role_lower or 'заместитель' in role_lower:
        return 'заместитель председателя'
    elif 'председатель' in role_lower or 'пред' in role_lower:
        return 'председатель'
    return role


def generate_protocol(applicant, exam_date):
    tpl = os.path.join(current_app.config['TEMPLATES_FOLDER'], 'protocol_template.docx')
    doc = Document(tpl)

    # 1. Улучшенный поиск председателя
    chairman = None
    for member in exam_date.commission:
        role_lower = member.role.lower()
        if 'председатель' in role_lower or 'пред' in role_lower:
            chairman = member
            break

    # Если не нашли явного председателя, берем первого в списке
    if not chairman and exam_date.commission:
        chairman = exam_date.commission[0]

    replacements = {
        '{chairman}': chairman.user.full_name if chairman else '',
        '{date}': translate_date_to_ru(exam_date.date.strftime('«%d» %B %Yг.')),
        '{program_code}': exam_date.program.code,
        '{program_name}': exam_date.program.name,
        '{applicant_name}': applicant.full_name
    }
    print(replacements)
    # Универсальная замена во всех элементах документа
    for placeholder, value in replacements.items():
        replace_placeholder(doc, placeholder, value)

    # 2. Таблица комиссии
    for p in doc.paragraphs:
        if '{commission_table}' in p.text:
            # Сохраняем позицию для вставки
            parent = p._p.getparent()
            index = parent.index(p._p) + 1

            # Создаем таблицу с нужным количеством колонок
            tbl = OxmlElement('w:tbl')

            # Устанавливаем ширину таблицы 100% (5000 в twips)
            tblPr = OxmlElement('w:tblPr')
            tblW = OxmlElement('w:tblW')
            tblW.set(qn('w:w'), "5000")
            tblW.set(qn('w:type'), "pct")
            tblPr.append(tblW)

            # Границы таблицы
            tblBorders = OxmlElement('w:tblBorders')
            for border_name in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
                border = OxmlElement(f'w:{border_name}')
                border.set(qn('w:val'), 'single')
                border.set(qn('w:sz'), '4')
                border.set(qn('w:space'), '0')
                border.set(qn('w:color'), '000000')
                tblBorders.append(border)
            tblPr.append(tblBorders)
            tbl.append(tblPr)

            # Ширина колонок: 70% и 30%
            tblGrid = OxmlElement('w:tblGrid')
            col1 = OxmlElement('w:gridCol')
            col1.set(qn('w:w'), "3500")  # 10%
            col2 = OxmlElement('w:gridCol')
            col2.set(qn('w:w'), "1500")  # 80%
            tblGrid.append(col1)
            tblGrid.append(col2)
            tbl.append(tblGrid)

            # Создаем строку заголовков
            tr = OxmlElement('w:tr')
            for header in ['ФИО', 'Должность']:
                tc = OxmlElement('w:tc')
                tcPr = OxmlElement('w:tcPr')
                tc.append(tcPr)

                p_elem = OxmlElement('w:p')
                r = OxmlElement('w:r')
                rPr = OxmlElement('w:rPr')

                b = OxmlElement('w:b')  # жирный заголовок
                rPr.append(b)

                rFonts = OxmlElement('w:rFonts')
                rFonts.set(qn('w:ascii'), 'Arial')
                rFonts.set(qn('w:hAnsi'), 'Arial')
                rPr.append(rFonts)

                sz = OxmlElement('w:sz')
                sz.set(qn('w:val'), "22")
                rPr.append(sz)

                r.append(rPr)
                t = OxmlElement('w:t')
                t.text = header
                r.append(t)
                p_elem.append(r)
                tc.append(p_elem)
                tr.append(tc)
            tbl.append(tr)
            #
            # Добавляем данные
            for member in exam_date.commission:
                tr = OxmlElement('w:tr')

                tc = OxmlElement('w:tc')
                tcPr = OxmlElement('w:tcPr')
                tc.append(tcPr)

                p_elem = OxmlElement('w:p')
                r = OxmlElement('w:r')
                rPr = OxmlElement('w:rPr')

                rFonts = OxmlElement('w:rFonts')
                rFonts.set(qn('w:ascii'), 'Arial')
                rFonts.set(qn('w:hAnsi'), 'Arial')
                rPr.append(rFonts)

                sz = OxmlElement('w:sz')
                sz.set(qn('w:val'), "22")
                rPr.append(sz)

                r.append(rPr)
                t = OxmlElement('w:t')
                t.text = member.user.full_name
                r.append(t)
                p_elem.append(r)
                tc.append(p_elem)
                tr.append(tc)
                tc = OxmlElement('w:tc')
                tcPr = OxmlElement('w:tcPr')
                tc.append(tcPr)

                p_elem = OxmlElement('w:p')
                r = OxmlElement('w:r')
                rPr = OxmlElement('w:rPr')

                rFonts = OxmlElement('w:rFonts')
                rFonts.set(qn('w:ascii'), 'Arial')
                rFonts.set(qn('w:hAnsi'), 'Arial')
                rPr.append(rFonts)

                sz = OxmlElement('w:sz')
                sz.set(qn('w:val'), "22")
                rPr.append(sz)

                r.append(rPr)
                t = OxmlElement('w:t')
                t.text = format_role(member.role)
                r.append(t)
                p_elem.append(r)
                tc.append(p_elem)
                tr.append(tc)
                tbl.append(tr)



            # Вставляем таблицу после параграфа с плейсхолдером
            parent.insert(index, tbl)

            # Удаляем плейсхолдер
            p.text = p.text.replace('{commission_table}', '')
            break

    # 3. Таблица вопросов
    total = 0
    for p in doc.paragraphs:
        if '{questions_table}' in p.text:
            parent = p._p.getparent()
            index = parent.index(p._p) + 1

            tbl = OxmlElement('w:tbl')

            # Ширина таблицы 100%
            tblPr = OxmlElement('w:tblPr')
            tblW = OxmlElement('w:tblW')
            tblW.set(qn('w:w'), "5000")
            tblW.set(qn('w:type'), "pct")
            tblPr.append(tblW)

            tblBorders = OxmlElement('w:tblBorders')
            for border_name in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
                border = OxmlElement(f'w:{border_name}')
                border.set(qn('w:val'), 'single')
                border.set(qn('w:sz'), '4')
                border.set(qn('w:space'), '0')
                border.set(qn('w:color'), '000000')
                tblBorders.append(border)
            tblPr.append(tblBorders)
            tbl.append(tblPr)

            # Ширина колонок: 10%, 80%, 10%
            tblGrid = OxmlElement('w:tblGrid')
            col1 = OxmlElement('w:gridCol')
            col1.set(qn('w:w'), "100")  # 10%
            col2 = OxmlElement('w:gridCol')
            col2.set(qn('w:w'), "4400")  # 80%
            col3 = OxmlElement('w:gridCol')
            col3.set(qn('w:w'), "500")  # 10%
            tblGrid.append(col1)
            tblGrid.append(col2)
            tblGrid.append(col3)
            tbl.append(tblGrid)

            # Заголовки
            tr = OxmlElement('w:tr')
            for header in ['№', 'Вопрос', 'Балл']:
                tc = OxmlElement('w:tc')
                tcPr = OxmlElement('w:tcPr')
                tc.append(tcPr)

                p_elem = OxmlElement('w:p')
                r = OxmlElement('w:r')
                rPr = OxmlElement('w:rPr')

                b = OxmlElement('w:b')  # жирный заголовок
                rPr.append(b)

                rFonts = OxmlElement('w:rFonts')
                rFonts.set(qn('w:ascii'), 'Arial')
                rFonts.set(qn('w:hAnsi'), 'Arial')
                rPr.append(rFonts)

                sz = OxmlElement('w:sz')
                sz.set(qn('w:val'), "22")
                rPr.append(sz)

                r.append(rPr)
                t = OxmlElement('w:t')
                t.text = header
                r.append(t)
                p_elem.append(r)
                tc.append(p_elem)
                tr.append(tc)
            tbl.append(tr)

            # Данные
            for i, score in enumerate(applicant.scores, start=1):
                tr = OxmlElement('w:tr')
                for value in [str(i), score.question.text, str(score.score)]:
                    tc = OxmlElement('w:tc')
                    tcPr = OxmlElement('w:tcPr')
                    tc.append(tcPr)

                    p_elem = OxmlElement('w:p')
                    r = OxmlElement('w:r')
                    rPr = OxmlElement('w:rPr')

                    rFonts = OxmlElement('w:rFonts')
                    rFonts.set(qn('w:ascii'), 'Arial')
                    rFonts.set(qn('w:hAnsi'), 'Arial')
                    rPr.append(rFonts)

                    sz = OxmlElement('w:sz')
                    sz.set(qn('w:val'), "22")
                    rPr.append(sz)

                    r.append(rPr)
                    t = OxmlElement('w:t')
                    t.text = value
                    r.append(t)
                    p_elem.append(r)
                    tc.append(p_elem)
                    tr.append(tc)
                tbl.append(tr)
                total += score.score

            # Итоговая строка
            tr = OxmlElement('w:tr')
            for value in ['ИТОГО', '', str(total)]:
                tc = OxmlElement('w:tc')
                tcPr = OxmlElement('w:tcPr')
                tc.append(tcPr)

                p_elem = OxmlElement('w:p')
                r = OxmlElement('w:r')
                rPr = OxmlElement('w:rPr')

                rFonts = OxmlElement('w:rFonts')
                rFonts.set(qn('w:ascii'), 'Arial')
                rFonts.set(qn('w:hAnsi'), 'Arial')
                rPr.append(rFonts)

                sz = OxmlElement('w:sz')
                sz.set(qn('w:val'), "22")
                rPr.append(sz)

                r.append(rPr)
                t = OxmlElement('w:t')
                t.text = value
                r.append(t)
                p_elem.append(r)
                tc.append(p_elem)
                tr.append(tc)
            tbl.append(tr)

            # Вставляем таблицу
            parent.insert(index, tbl)

            # Удаляем плейсхолдер
            p.text = p.text.replace('{questions_table}', '')
            break

    # 4. Замена общего балла
    for p in doc.paragraphs:
        if '{total_score}' in p.text:
            p.text = p.text.replace('{total_score}', str(total))

    # 5. Подписи комиссии с должностями
    signatures_added = False
    for p in doc.paragraphs:
        if '{signatures}' in p.text:
            # Сохраняем выравнивание оригинала
            alignment = p.paragraph_format.alignment

            # Очищаем параграф
            p.text = ''

            # Сортируем комиссию: председатель, заместитель, члены
            sorted_commission = sorted(
                exam_date.commission,
                key=lambda m: (
                    0 if m.role == 'председатель'
                    else 1 if m.role == 'заместитель'
                    else 2
                )
            )

            for member in sorted_commission:
                # Используем должность пользователя, если она указана
                position = member.user.position

                # Если должность не указана, используем роль
                if not position:
                    if member.role == 'председатель':
                        position = 'Председатель комиссии'
                    elif member.role == 'заместитель':
                        position = 'Заместитель председателя'
                    else:
                        position = 'Член комиссии'

                # Добавляем строку с подписью
                run = p.add_run(f"{position} ____________________ / {member.user.full_name} /")
                run.font.name = 'Arial'
                run.font.size = Pt(11)

                # Добавляем разрыв строки, кроме последней подписи
                if member != sorted_commission[-1]:
                    p.add_run().add_break()

            # Восстанавливаем выравнивание
            p.paragraph_format.alignment = alignment
            signatures_added = True
            break

    # Если не нашли плейсхолдер, добавляем в конец
    if not signatures_added:
        p = doc.add_paragraph()
        # Сортируем комиссию
        sorted_commission = sorted(
            exam_date.commission,
            key=lambda m: (
                0 if m.role == 'председатель'
                else 1 if m.role == 'заместитель'
                else 2
            )
        )

        for i, member in enumerate(sorted_commission):
            # Определяем должность
            position = member.user.position
            if not position:
                if member.role == 'председатель':
                    position = 'Председатель комиссии'
                elif member.role == 'заместитель':
                    position = 'Заместитель председателя'
                else:
                    position = 'Член комиссии'

            run = p.add_run(f"{position} ____________________ / {member.user.full_name} /")
            run.font.name = 'Arial'
            run.font.size = Pt(11)

            if i < len(sorted_commission) - 1:
                p.add_run().add_break()

    return doc


def generate_vedomost(exam_date):
    template_path = os.path.join(current_app.config['TEMPLATES_FOLDER'], 'vedomost_template.docx')
    doc = Document(template_path)

    chairman = None
    for member in exam_date.commission:
        role_lower = member.role.lower()
        if 'председатель' in role_lower or 'пред' in role_lower:
            chairman = member
            break

    # Если не нашли явного председателя, берем первого в списке
    if not chairman and exam_date.commission:
        chairman = exam_date.commission[0]

    chairman_name = chairman.user.full_name if chairman else ""

    replacements = {
        '{date}': exam_date.date.strftime('%d.%m.%Y'),
        '{program_code}': exam_date.program.code,
        '{program_name}': exam_date.program.name,
        '{chairman}': chairman_name
    }

    for p in doc.paragraphs:
        for key, value in replacements.items():
            if key in p.text:
                p.text = p.text.replace(key, value)

    # Заполнение таблицы абитуриентов (первая таблица)
    if len(doc.tables) > 0:
        table = doc.tables[0]
        # Удаляем вторую строку (шаблонную)
        if len(table.rows) > 1:
            table._tbl.remove(table.rows[1]._tr)
        for i, applicant in enumerate(exam_date.applicants):
            total_score = sum(score.score for score in applicant.scores)
            row = table.add_row().cells
            row[0].text = str(i + 1)
            row[1].text = applicant.full_name
            row[2].text = str(total_score)

            # Установка шрифта Arial 11pt для ячеек
            for cell in row:
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.font.name = 'Arial'
                        run.font.size = Pt(11)

    # Добавляем подписи членов комиссии (после таблицы)
    # Сортируем комиссию: председатель, заместитель, члены
    sorted_commission = sorted(
        exam_date.commission,
        key=lambda m: (
            0 if m.role == 'председатель'
            else 1 if m.role == 'заместитель'
            else 2
        )
    )

    members_text = "Члены экзаменационной комиссии:\n"
    for member in sorted_commission:
        if member.role == 'председатель':
            continue  # председатель уже в шапке

        # Используем должность пользователя, если она указана
        position = member.user.position

        # Если должность не указана, используем роль
        if not position:
            if member.role == 'заместитель':
                position = 'Заместитель председателя'
            else:
                position = 'Член комиссии'

        members_text += f"{position} ____________________ / {member.user.full_name} /\n"

    # Добавляем параграф с подписями
    p = doc.add_paragraph(members_text)

    # Устанавливаем шрифт Arial 11pt
    for run in p.runs:
        run.font.name = 'Arial'
        run.font.size = Pt(11)

    return doc