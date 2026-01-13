def canvas_para_video(x_canvas, y_canvas, img_geometria, scale_factor, offset_borda=0):
    """
    Converte coordenadas do Canvas da UI para coordenadas do Vídeo (base 360p).
    img_geometria: (img_x, img_y, img_w, img_h) do preview no canvas.
    """
    img_x, img_y, _, _ = img_geometria
    
    # Converter clique do canvas para coordenadas do vídeo renderizado (escala do preview)
    video_render_x = (x_canvas - img_x) / scale_factor
    video_render_y = (y_canvas - img_y) / scale_factor
    
    # Remover o offset da borda para obter a coordenada original (base 360p)
    x_video = video_render_x - offset_borda
    y_video = video_render_y - offset_borda
    
    return int(x_video), int(y_video)

def video_para_canvas(x_video, y_video, img_geometria, scale_factor, offset_borda=0):
    """
    Converte coordenadas do Vídeo (base 360p) para coordenadas do Canvas da UI.
    """
    img_x, img_y, _, _ = img_geometria
    
    # Aplicar offset da borda
    video_render_x = x_video + offset_borda
    video_render_y = y_video + offset_borda
    
    # Converter para pixels do canvas
    x_canvas = video_render_x * scale_factor + img_x
    y_canvas = video_render_y * scale_factor + img_y
    
    return int(x_canvas), int(y_canvas)
