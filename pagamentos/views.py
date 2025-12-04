from django.shortcuts import render, redirect, get_object_or_404  
from django.db import connection, transaction
from django.contrib import messages
from django.utils import timezone
from datetime import date
from .forms import *
from .models import Compra, Pagamento, Factura, FacturaLinha
from pacotes.models import Pacote, Hotel, Voo, PacoteHotel, PacoteVoo
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from io import BytesIO
from django.http import HttpResponse
from django.db.models import Q

# Create your views here.
def processar_pagamento(request, pacote_id, hotel_id, voo_id):
    """
    Página de seleção de método de pagamento e processamento da compra
    """
    pacote = get_object_or_404(Pacote, pacote_id=pacote_id)
    hotel = get_object_or_404(Hotel, hotel_id=hotel_id)
    voo = get_object_or_404(Voo, voo_id=voo_id)
    
    # Calcular preços
    num_noites = (pacote.data_fim - pacote.data_inicio).days
    preco_hotel_total = hotel.preco_diario * num_noites
    preco_voo_total = voo.preco
    preco_base_pacote = pacote.preco_total
    preco_total_final = preco_base_pacote + preco_hotel_total + preco_voo_total
    
    if request.method == "POST":
        form = MetodoPagamentoForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    metodo = form.cleaned_data['metodo']
                    
                    # 1. Criar a Compra
                    compra = Compra.objects.create(
                        user=request.user,
                        pacote=pacote,
                        data_compra=date.today(),
                        valor_total=preco_total_final,
                        estado='Confirmada'
                    )
                    
                    # 2. Criar o Pagamento
                    pagamento = Pagamento.objects.create(
                        compra_id=compra.compra_id,
                        data_pagamento=date.today(),
                        valor=preco_total_final,
                        estado='Aprovado',
                        metodo=metodo
                    )
                    
                    # 3. Atualizar a compra com o ID do pagamento
                    compra.pagamento_id = pagamento.pagamento_id
                    compra.save()
                    
                    # 4. Criar a Fatura
                    fatura = Factura.objects.create(
                        compra_id=compra,
                        pagamento_id=pagamento,
                        data_emissao=timezone.now(),
                        valor_total=preco_total_final
                    )
                    
                    # 5. Criar as Linhas da Fatura
                    # Linha 1: Pacote base
                    FacturaLinha.objects.create(
                        fatura=fatura,
                        pacote=pacote,
                        descricao_item=f"Pacote Base - {pacote.nome}",
                        preco=preco_base_pacote,
                        subtotal=preco_base_pacote
                    )
                    
                    # Linha 2: Hotel
                    FacturaLinha.objects.create(
                        fatura=fatura,
                        pacote=pacote,
                        descricao_item=f"Hotel - {hotel.nome} ({num_noites} noite{'s' if num_noites > 1 else ''})",
                        preco=hotel.preco_diario,
                        subtotal=preco_hotel_total
                    )
                    
                    # Linha 3: Voo
                    FacturaLinha.objects.create(
                        fatura=fatura,
                        pacote=pacote,
                        descricao_item=f"Voo - {voo.companhia}",
                        preco=preco_voo_total,
                        subtotal=preco_voo_total
                    )
                    
                    # 6. Associar Hotel e Voo ao Pacote
                    PacoteHotel.objects.get_or_create(
                        pacote_id=pacote,
                        hotel_id=hotel
                    )
                    
                    PacoteVoo.objects.get_or_create(
                        pacote_id=pacote,
                        voo_id=voo
                    )
                    
                    # Redirecionar para página de sucesso
                    return redirect('compra_sucesso', compra_id=compra.compra_id)
                    
            except Exception as e:
                messages.error(request, f'Erro ao processar pagamento: {str(e)}')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        form = MetodoPagamentoForm()
    
    return render(request, "processar_pagamento.html", {
        "form": form,
        "pacote": pacote,
        "hotel": hotel,
        "voo": voo,
        "num_noites": num_noites,
        "preco_hotel_total": preco_hotel_total,
        "preco_voo_total": preco_voo_total,
        "preco_base_pacote": preco_base_pacote,
        "preco_total_final": preco_total_final,
    })


def compra_sucesso(request, compra_id):
    """
    Página de confirmação de compra realizada com sucesso
    """
    compra = get_object_or_404(Compra, compra_id=compra_id)
    
    # Verificar se a compra pertence ao usuário logado
    if compra.user != request.user:
        messages.error(request, 'Acesso negado.')
        return redirect('pacotes_por_pais')
    
    # Buscar fatura e suas linhas
    fatura = Factura.objects.filter(compra_id=compra).first()
    linhas_fatura = FacturaLinha.objects.filter(fatura=fatura) if fatura else []
    
    # Buscar pagamento
    pagamento = Pagamento.objects.filter(pagamento_id=compra.pagamento_id).first()
    
    return render(request, "compra_sucesso.html", {
        "compra": compra,
        "fatura": fatura,
        "linhas_fatura": linhas_fatura,
        "pagamento": pagamento,
    })


def compra_pdf(request, compra_id):
    """Gera PDF estilizado com detalhes da compra, pagamento e fatura."""
    compra = get_object_or_404(Compra, compra_id=compra_id)
    if compra.user != request.user:
        messages.error(request, 'Acesso negado.')
        return redirect('pacotes_por_pais')

    fatura = Factura.objects.filter(compra_id=compra).first()
    linhas_fatura = FacturaLinha.objects.filter(fatura=fatura) if fatura else []
    pagamento = Pagamento.objects.filter(pagamento_id=compra.pagamento_id).first()

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=40, rightMargin=40, topMargin=50, bottomMargin=40)
    styles = getSampleStyleSheet()
    elements = []

    title_style = styles['Title']
    title_style.fontSize = 20
    title_style.leading = 24
    elements.append(Paragraph('Resumo da Compra', title_style))
    elements.append(Spacer(1, 12))

    info_style = styles['Normal']
    info_style.fontSize = 11
    compra_info = (
        f"<b>ID Compra:</b> {compra.compra_id}<br/>"
        f"<b>Pacote:</b> {compra.pacote.nome}<br/>"
        f"<b>Data da Compra:</b> {compra.data_compra}<br/>"
        f"<b>Estado:</b> {compra.estado}<br/>"
        f"<b>Valor Total:</b> €{compra.valor_total}"
    )
    elements.append(Paragraph(compra_info, info_style))
    elements.append(Spacer(1, 14))

    if pagamento:
        elements.append(Paragraph('<b>Pagamento</b>', styles['Heading3']))
        pay_info = (
            f"<b>Método:</b> {pagamento.metodo}<br/>"
            f"<b>Estado:</b> {pagamento.estado}<br/>"
            f"<b>Data Pagamento:</b> {pagamento.data_pagamento}<br/>"
            f"<b>Valor Pago:</b> €{pagamento.valor}"
        )
        elements.append(Paragraph(pay_info, info_style))
        elements.append(Spacer(1, 12))

    if fatura:
        elements.append(Paragraph('<b>Fatura</b>', styles['Heading3']))
        elements.append(Paragraph(f"<b>Data Emissão:</b> {fatura.data_emissao}", info_style))
        elements.append(Spacer(1, 6))

        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.enums import TA_RIGHT

        header = ["Descrição", "Preço Unit.", "Subtotal"]
        table_rows = [header]

        normal_style = styles['Normal']
        right_style = ParagraphStyle('Right', parent=normal_style, alignment=TA_RIGHT)
        bold_right = ParagraphStyle('BoldRight', parent=right_style, fontName='Helvetica-Bold')

        for linha in linhas_fatura:
            table_rows.append([
                Paragraph(linha.descricao_item, normal_style),
                Paragraph(f"€{linha.preco}", right_style),
                Paragraph(f"€{linha.subtotal}", right_style)
            ])
        table_rows.append([
            Paragraph("", normal_style),
            Paragraph("Total:", bold_right),
            Paragraph(f"€{fatura.valor_total}", bold_right)
        ])

        tbl = Table(table_rows, colWidths=[260, 100, 100])
        tbl.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d6efd')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -2), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e9ecef')),
            ('ALIGN', (1, 1), (-1, -2), 'RIGHT'),
            ('ALIGN', (1, -1), (-1, -1), 'RIGHT'),
        ]))
        elements.append(tbl)
        elements.append(Spacer(1, 18))

    elements.append(Paragraph('Documento gerado automaticamente.', styles['Italic']))

    doc.build(elements)
    pdf_value = buffer.getvalue()
    buffer.close()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="compra_{compra.compra_id}.pdf"'
    response.write(pdf_value)
    return response


def pagamentos(request):
    """
    Lista todos os pagamentos com informação do cliente que pagou
    """
    # Buscar todos os pagamentos
    pagamentos_list = Pagamento.objects.all()
    
    # Preparar lista com dados estruturados
    pagamentos_data = []
    for pag in pagamentos_list:
        # Buscar compra relacionada pelo IntegerField compra_id
        compra = Compra.objects.filter(compra_id=pag.compra_id).select_related('user').first()
        cliente_nome = "N/A"
        if compra and compra.user:
            cliente_nome = f"{compra.user.firstname} {compra.user.lastname}".strip()
            if not cliente_nome:
                cliente_nome = compra.user.email
        
        pagamentos_data.append({
            'pagamento_id': pag.pagamento_id,
            'cliente_nome': cliente_nome,
            'valor': pag.valor,
            'data_pagamento': pag.data_pagamento,
            'estado': pag.estado,
            'metodo': pag.metodo,
        })
    
    # Filtrar por query param 'q' (nome do cliente)
    q = request.GET.get('q', '').strip()
    if q:
        pagamentos_data = [
            p for p in pagamentos_data 
            if q.lower() in p['cliente_nome'].lower()
        ]
    
    return render(request, 'pagamentos.html', {
        'pagamentos': pagamentos_data
    })
#---------------------------------------------------------------#

def faturas(request):
    """
    Lista todas as faturas com informações completas
    """
    # Buscar faturas com relacionamentos
    faturas_list = Factura.objects.select_related(
        'compra_id__user',
        'pagamento_id'
    ).all()
    
    # Preparar lista com dados estruturados
    faturas_data = []
    for fatura in faturas_list:
        compra = fatura.compra_id
        pagamento = fatura.pagamento_id
        
        # Nome do cliente
        cliente_nome = "N/A"
        if compra and compra.user:
            cliente_nome = f"{compra.user.firstname} {compra.user.lastname}".strip()
            if not cliente_nome:
                cliente_nome = compra.user.email
        
        faturas_data.append({
            'fatura_id': fatura.fatura_id,
            'nome_cliente': cliente_nome,
            'data_emissao': fatura.data_emissao,
            'valor_total': fatura.valor_total,
            'tipo_pagamento': pagamento.metodo if pagamento else None,
            'estado_pagamento': pagamento.estado if pagamento else None,
        })
    
    return render(request, 'faturas.html', {
        'faturas': faturas_data
    })


def fatura_detalhes(request, fatura_id):
    """
    Exibe detalhes completos de uma fatura
    """
    try:
        fatura = Factura.objects.select_related(
            'compra_id__user',
            'compra_id__pacote',
            'pagamento_id'
        ).get(fatura_id=fatura_id)
        
        # Buscar linhas da fatura
        linhas = FacturaLinha.objects.filter(fatura=fatura)
        
        # Preparar dados da fatura
        compra = fatura.compra_id
        pagamento = fatura.pagamento_id
        
        fatura_data = {
            'fatura_id': fatura.fatura_id,
            'data_emissao': fatura.data_emissao,
            'valor_total': fatura.valor_total,
            'estado_pagamento': pagamento.estado if pagamento else 'N/A',
            'tipo_pagamento': pagamento.metodo if pagamento else None,
            'compra_id': compra.compra_id if compra else None,
            'pagamento_id': pagamento.pagamento_id if pagamento else None,
            'nome_cliente': f"{compra.user.firstname} {compra.user.lastname}".strip() if compra and compra.user else 'N/A',
            'email': compra.user.email if compra and compra.user else 'N/A',
            'user_id': compra.user.user_id if compra and compra.user else None,
        }
        
        # Preparar linhas da fatura com informações detalhadas
        linhas_data = []
        for linha in linhas:
            # Extrair tipo de item da descrição
            tipo_item = "Item"
            if "Pacote Base" in linha.descricao_item:
                tipo_item = "Pacote Base"
            elif "Hotel" in linha.descricao_item:
                tipo_item = "Alojamento"
            elif "Voo" in linha.descricao_item:
                tipo_item = "Voo"
            
            linhas_data.append({
                'tipo': tipo_item,
                'descricao': linha.descricao_item,
                'quantidade': 1,
                'preco_unitario': linha.preco,
                'subtotal': linha.subtotal
            })
        
        return render(request, 'fatura_detalhes.html', {
            'fatura': fatura_data,
            'linhas': linhas_data
        })
        
    except Factura.DoesNotExist:
        return render(request, 'fatura_detalhes.html', {
            'error': 'Fatura não encontrada.'
        })


def fatura_pdf(request, fatura_id):
    """Gera PDF com detalhes da fatura."""
    fatura = get_object_or_404(Factura, fatura_id=fatura_id)
    
    linhas_fatura = FacturaLinha.objects.filter(fatura=fatura)
    pagamento = fatura.pagamento_id
    compra = fatura.compra_id

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=40, rightMargin=40, topMargin=50, bottomMargin=40)
    styles = getSampleStyleSheet()
    elements = []

    title_style = styles['Title']
    title_style.fontSize = 20
    title_style.leading = 24
    elements.append(Paragraph(f'Fatura #{fatura.fatura_id}', title_style))
    elements.append(Spacer(1, 12))

    info_style = styles['Normal']
    info_style.fontSize = 11
    
    # Informações do cliente
    cliente_nome = "N/A"
    if compra and compra.user:
        cliente_nome = f"{compra.user.firstname} {compra.user.lastname}".strip()
        if not cliente_nome:
            cliente_nome = compra.user.email
    
    fatura_info = (
        f"<b>Cliente:</b> {cliente_nome}<br/>"
        f"<b>Data de Emissão:</b> {fatura.data_emissao.strftime('%d/%m/%Y %H:%M')}<br/>"
        f"<b>ID Compra:</b> {compra.compra_id if compra else 'N/A'}<br/>"
        f"<b>Data da Compra:</b> {compra.data_compra if compra else 'N/A'}"
    )
    elements.append(Paragraph(fatura_info, info_style))
    elements.append(Spacer(1, 14))

    if pagamento:
        elements.append(Paragraph('<b>Informações de Pagamento</b>', styles['Heading3']))
        pay_info = (
            f"<b>Método:</b> {pagamento.metodo}<br/>"
            f"<b>Estado:</b> {pagamento.estado}<br/>"
            f"<b>Data Pagamento:</b> {pagamento.data_pagamento}<br/>"
            f"<b>Valor Pago:</b> €{pagamento.valor}"
        )
        elements.append(Paragraph(pay_info, info_style))
        elements.append(Spacer(1, 12))

    # Tabela de linhas da fatura
    elements.append(Paragraph('<b>Detalhes da Fatura</b>', styles['Heading3']))
    elements.append(Spacer(1, 6))

    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_RIGHT

    header = ["Descrição", "Preço Unit.", "Subtotal"]
    table_rows = [header]

    normal_style = styles['Normal']
    right_style = ParagraphStyle('Right', parent=normal_style, alignment=TA_RIGHT)
    bold_right = ParagraphStyle('BoldRight', parent=right_style, fontName='Helvetica-Bold')

    for linha in linhas_fatura:
        table_rows.append([
            Paragraph(linha.descricao_item, normal_style),
            Paragraph(f"€{linha.preco}", right_style),
            Paragraph(f"€{linha.subtotal}", right_style)
        ])
    
    table_rows.append([
        Paragraph("", normal_style),
        Paragraph("Total:", bold_right),
        Paragraph(f"€{fatura.valor_total}", bold_right)
    ])

    tbl = Table(table_rows, colWidths=[260, 100, 100])
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d6efd')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -2), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e9ecef')),
        ('ALIGN', (1, 1), (-1, -2), 'RIGHT'),
        ('ALIGN', (1, -1), (-1, -1), 'RIGHT'),
    ]))
    elements.append(tbl)
    elements.append(Spacer(1, 18))

    elements.append(Paragraph('Documento gerado automaticamente.', styles['Italic']))

    doc.build(elements)
    pdf_value = buffer.getvalue()
    buffer.close()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="fatura_{fatura.fatura_id}.pdf"'
    response.write(pdf_value)
    return response


# def fatura_detalhes(request, fatura_id):
#     """
#     Mostra os detalhes completos de uma fatura incluindo todas as suas linhas
#     (SQL DIRETO - SUA PARTE - usando FUNCTIONs da BD)
#     """
#     with connection.cursor() as cursor:
#         # Buscar informações da fatura usando FUNCTION
#         cursor.execute("SELECT * FROM get_fatura_detalhes(%s)", [fatura_id])
#         columns = [col[0] for col in cursor.description]
#         result = cursor.fetchone()
        
#         if not result:
#             return render(request, 'fatura_detalhes.html', {
#                 'error': 'Fatura não encontrada'
#             })
        
#         fatura = dict(zip(columns, result))
        
#         # Buscar linhas da fatura usando FUNCTION
#         cursor.execute("SELECT * FROM get_fatura_linhas(%s)", [fatura_id])
#         columns = [col[0] for col in cursor.description]
#         linhas = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
#     return render(request, 'fatura_detalhes.html', {
#         'fatura': fatura,
#         'linhas': linhas
#     })


