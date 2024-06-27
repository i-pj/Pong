import pygame

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

def create_menu(screen):
    font = pygame.font.Font(None, 36)

    # Center buttons
    screen_rect = screen.get_rect()
    center_x = screen_rect.centerx
    center_y = screen_rect.centery

    # Create rectangles
    button_vs_computer = pygame.Rect(center_x - 100, center_y - 75, 200, 50)
    button_vs_player = pygame.Rect(center_x - 100, center_y + 25, 200, 50)

    # Render text
    text_vs_computer = font.render("vs Computer", True, (255, 255, 255))
    text_vs_player = font.render("vs Player", True, (255, 255, 255))

    selected_button = 1  # Default selection

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_button = (selected_button - 1) % 2
                elif event.key == pygame.K_DOWN:
                    selected_button = (selected_button + 1) % 2
                elif event.key == pygame.K_RETURN:
                    if selected_button == 1:
                        return "vs_computer"
                    else:
                        return "vs_player"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_vs_computer.collidepoint(event.pos):
                    return "vs_computer"
                elif button_vs_player.collidepoint(event.pos):
                    return "vs_player"

        # Draw
        screen.fill((0, 0, 0))
        if selected_button == 0:
            pygame.draw.rect(screen, (0, 0, 0), button_vs_computer)
        else:
            pygame.draw.rect(screen, (255, 255, 255), button_vs_computer, 2)
        if selected_button == 1:
            pygame.draw.rect(screen, (0, 0, 0), button_vs_player)
        else:
            pygame.draw.rect(screen, (255, 255, 255), button_vs_player, 2)
        screen.blit(text_vs_computer, (button_vs_computer.x + 10, button_vs_computer.y + 10))
        screen.blit(text_vs_player, (button_vs_player.x + 10, button_vs_player.y + 10))
        pygame.display.flip()

    return None
