from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import time
import math

window_width = 1440
window_height = 750

# Camera-related variables
camera_mode = 'fps'
fovY = 75  # Field of view
camera_pitch = 0


mouse_center_x = window_width // 2
mouse_center_y = window_height // 2
cursor_locked = True
mouse_sensitivity = 0.4

current_time = time.time()
delta_time = None

player_pos = [0,100,200]
player_angle = 0
player_width = 20
player_height = 40

player_normal_movement_velocity = 200
player_forward_velocity_multiplier = 0.0
player_sideward_velocity_multiplier = 0.0
player_upward_velocity_multiplier = 0.0
player_acceleration = 4
player_gravity = 45
player_jump_force = 26

movement_keys_pressed = {'w': False, 's': False, 'a': False, 'd': False, 'space': False}

world_ground_level = 25
grid_dimension = (100,100)
tile_length = 10
tile_res = 1
grid_color = [0.2,0.4,0.4]
wall_cubeoid_res = 2
flashlight_tiles_radius = 25
flashlight_radius = tile_length * flashlight_tiles_radius
flashlight_radius_squared = flashlight_radius ** 2

weapon_bullet_ray_origin_pos = [0,0,0]
weapon_muzzle_pos = [0,0,0]



tiles_dict = {}

bullets = []

def draw_tile(tile_x, tile_y, tile_z, tile_info_dict):
    tiles_dict[(tile_x, tile_y, tile_z)] = tile_info_dict

def draw_wall(wall_start_tile_x, wall_start_tile_y, wall_start_tile_z, wall_tile_width, wall_tile_length, wall_tile_height, wall_info_dict):
    global tiles_dict

    #right wall
    cur_tile_y = wall_start_tile_y
    while cur_tile_y < wall_start_tile_y + wall_tile_length:
        cur_tile_z = wall_start_tile_z
        while cur_tile_z < wall_start_tile_z + wall_tile_height:
            draw_tile(wall_start_tile_x, cur_tile_y, cur_tile_z, wall_info_dict)
            cur_tile_z += 1
        cur_tile_y += 1

    #left wall
    cur_tile_y = wall_start_tile_y
    while cur_tile_y < wall_start_tile_y + wall_tile_length:
        cur_tile_z = wall_start_tile_z
        while cur_tile_z < wall_start_tile_z + wall_tile_height:
            draw_tile(wall_start_tile_x + wall_tile_width - 1, cur_tile_y, cur_tile_z, wall_info_dict)
            cur_tile_z += 1
        cur_tile_y += 1

    #top wall
    cur_tile_x = wall_start_tile_x
    while cur_tile_x < wall_start_tile_x + wall_tile_width:
        cur_tile_z = wall_start_tile_z
        while cur_tile_z < wall_start_tile_z + wall_tile_height:
            draw_tile(cur_tile_x, wall_start_tile_y, cur_tile_z, wall_info_dict)
            cur_tile_z += 1
        cur_tile_x += 1

    #bottom wall
    cur_tile_x = wall_start_tile_x
    while cur_tile_x < wall_start_tile_x + wall_tile_width:
        cur_tile_z = wall_start_tile_z
        while cur_tile_z < wall_start_tile_z + wall_tile_height:
            draw_tile(cur_tile_x, wall_start_tile_y + wall_tile_length - 1, cur_tile_z, wall_info_dict)
            cur_tile_z += 1
        cur_tile_x += 1


    #floor
    cur_tile_y = wall_start_tile_y
    while cur_tile_y < wall_start_tile_y + wall_tile_length:
        cur_tile_x = wall_start_tile_x
        while cur_tile_x < wall_start_tile_x + wall_tile_width:
            draw_tile(cur_tile_x, cur_tile_y, wall_start_tile_z, wall_info_dict)
            cur_tile_x += 1
        cur_tile_y += 1


    #ceiling
    cur_tile_y = wall_start_tile_y
    while cur_tile_y < wall_start_tile_y + wall_tile_length:
        cur_tile_x = wall_start_tile_x
        while cur_tile_x < wall_start_tile_x + wall_tile_width:
            draw_tile(cur_tile_x, cur_tile_y, wall_start_tile_z + wall_tile_height, wall_info_dict)
            cur_tile_x += 1
        cur_tile_y +=1


def draw_floor():
    for x in range(grid_dimension[0]):
        for y in range(grid_dimension[1]):
            draw_tile(x, y, 0, {'color': grid_color})

def is_tile_occupied(tile_x, tile_y, tile_z):
    return (tile_x, tile_y, tile_z) in tiles_dict

def get_tile_from_pos(pos_x, pos_y, pos_z):
    init_x = - (tile_length * grid_dimension[0]) / 2
    init_y = - (tile_length * grid_dimension[1]) / 2
    
    tile_x = int((pos_x - init_x)/tile_length)
    tile_y = int((pos_y - init_y)/tile_length)
    tile_z = int(pos_z / tile_length)

    return (tile_x, tile_y, tile_z)

def loadMap():
    draw_floor()
    draw_wall(5,90,0,50,4, 15, {'color': (0,1,0)})
    draw_wall(40,42,0,55,4, 5, {'color': (0,1,0)})
    draw_wall(5,5,0,5,2, 15, {'color': (1,0,0)})
    draw_wall(10,50,0,2,25, 15, {'color': (0,1,0)})
    draw_wall(55,70,0,25,10, 15, {'color': (0,1,0)})

def move_player(movement_vector_x, movement_vector_y, movement_vector_z):
    cur_x, cur_y, cur_z = player_pos
    new_x = cur_x + movement_vector_x
    new_y = cur_y + movement_vector_y
    new_z = cur_z + movement_vector_z

    #detect collision left side of body
    x = new_x + player_width / 2
    y = new_y
    z = new_z

    tile_x, tile_y, tile_z = get_tile_from_pos(x, y, z)
    if is_tile_occupied(tile_x, tile_y, tile_z):
        return

    #detect collision right side of body
    x = new_x - player_width / 2
    y = new_y
    z = new_z

    tile_x, tile_y, tile_z = get_tile_from_pos(x, y, z)
    if is_tile_occupied(tile_x, tile_y, tile_z):
        return

    #detect collision front side of body
    x = new_x
    y = new_y - player_width / 2
    z = new_z

    tile_x, tile_y, tile_z = get_tile_from_pos(x, y, z)
    if is_tile_occupied(tile_x, tile_y, tile_z):
        return

    #detect collision back side of body
    x = new_x
    y = new_y + player_width / 2
    z = new_z

    tile_x, tile_y, tile_z = get_tile_from_pos(x, y, z)
    if is_tile_occupied(tile_x, tile_y, tile_z):
        return


    player_pos[0] = new_x
    player_pos[1] = new_y
    player_pos[2] = new_z

def is_player_grounded():
    # return player_pos[2] <= world_ground_level

    tile_x, tile_y, tile_z = get_tile_from_pos(player_pos[0], player_pos[1], player_pos[2] - player_height)
    return is_tile_occupied(tile_x, tile_y, tile_z) or player_pos[2] - player_height <= world_ground_level

def get_player_forward_vector():
    global player_angle
    x = math.sin(player_angle * math.pi / 180)
    y = - math.cos(player_angle * math.pi / 180)

    return (x,y)

def get_player_aim_vector():
    x = math.sin(player_angle * math.pi / 180) * math.cos(camera_pitch * math.pi/180)
    y = - math.cos(player_angle * math.pi / 180) * math.cos(camera_pitch * math.pi/180)
    z = math.sin(camera_pitch * math.pi/180)
    return (x,y,z)

def get_distance_squared(pos_1, pos_2):
    pos_1_x, pos_1_y, pos_1_z = pos_1
    pos_2_x, pos_2_y, pos_2_z = pos_2

    res = (pos_1_x - pos_2_x)**2 + (pos_1_y - pos_2_y)**2 + (pos_1_z - pos_2_z)**2
    return res

def get_adjusted_object_color(object_position, preferred_color):
    distance_from_player_squared = get_distance_squared(object_position, player_pos)
    brightness_value = (flashlight_radius_squared - distance_from_player_squared) / (flashlight_radius_squared + 0.75* distance_from_player_squared)
    return (preferred_color[0] * brightness_value, preferred_color[1] * brightness_value, preferred_color[2] * brightness_value)

def should_objected_be_rendered(object_pos):
    object_distance_from_player_squared = get_distance_squared(player_pos, object_pos)
    return object_distance_from_player_squared < flashlight_radius_squared

def should_illuminated_objected_be_rendered(object_pos):
    object_distance_from_player_squared = get_distance_squared(player_pos, object_pos)
    return object_distance_from_player_squared < flashlight_radius_squared * 4

def drawCrosshair():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, window_width, 0, window_height)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glColor3f(1, 1, 1)

    glBegin(GL_LINES)

    cross_hair_len = 10
    # Horizontal
    glVertex2f(window_width/2 - cross_hair_len, window_height/2)
    glVertex2f(window_width/2 + cross_hair_len, window_height/2)

    # Vertical
    glVertex2f(window_width/2 , window_height/2 - cross_hair_len)
    glVertex2f(window_width/2 , window_height/2 + cross_hair_len)

    glEnd()

    glPopMatrix()

    glMatrixMode(GL_PROJECTION)
    glPopMatrix()

    glMatrixMode(GL_MODELVIEW)

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1,1,1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    
    # Set up an orthographic projection that matches window coordinates
    gluOrtho2D(0, 1000, 0, 800)  # left, right, bottom, top

    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Draw text at (x, y) in screen coordinates
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    
    # Restore original projection and modelview matrices
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def render_tiles():
    global tiles_dict
    
    world_start_pos_x = - (tile_length * grid_dimension[0]) / 2
    world_start_pos_y = - (tile_length * grid_dimension[1]) / 2

    tileoid_length = tile_length / tile_res

    render_center_x, render_center_y, render_center_z = get_tile_from_pos(player_pos[0], player_pos[1], player_pos[2])
    render_radius = int(flashlight_radius / tile_length)
    for x in range(render_center_x - render_radius, render_center_x + render_radius + 1):
        for y in range(render_center_y - render_radius, render_center_y + render_radius + 1):
            for z in range(render_center_z - render_radius, render_center_z + render_radius + 1):
                if (x,y,z) not in tiles_dict:
                    continue

                tile_pos_x, tile_pos_y, tile_pos_z = (x,y,z)
                tile_info_dict = tiles_dict[(x,y,z)]

                tile_start_x = world_start_pos_x + tile_pos_x * tile_length
                tile_end_x = tile_start_x + tile_length

                tile_start_y = world_start_pos_y + tile_pos_y * tile_length
                tile_end_y = tile_start_y + tile_length

                tile_start_z = tile_pos_z * tile_length
                tile_end_z = tile_start_z + tile_length

                cur_y = tile_start_y

                while cur_y < tile_end_y:
                    cur_x = tile_start_x

                    while cur_x < tile_end_x:
                        cur_z = tile_start_z

                        while cur_z < tile_end_z:

                            if should_objected_be_rendered((cur_x + tileoid_length/2, cur_y + tileoid_length/2, cur_z + tileoid_length/2)):
                                tileoid_color_r, tileoid_color_g, tileoid_color_b = get_adjusted_object_color((cur_x + tileoid_length/2, cur_y + tileoid_length/2, cur_z + tileoid_length/2), tile_info_dict['color'])
                                glPushMatrix()
                                glColor3f(tileoid_color_r, tileoid_color_g , tileoid_color_b)
                                glTranslatef(cur_x + tileoid_length / 2, cur_y + tileoid_length/2, cur_z + tileoid_length/2)
                                glScale(tileoid_length, tileoid_length, tileoid_length)
                                glutSolidCube(1)
                                glPopMatrix()

                            cur_z += tileoid_length
                        cur_x += tileoid_length
                    cur_y += tileoid_length

def drawPlayer():
    player_x, player_y, player_z = player_pos
    glPushMatrix()
    glColor3f(1, 0, 0)
    glTranslatef(player_x, player_y, player_z)
    glRotatef(player_angle, 0, 0, 1)
    
    glutSolidCube(20)
    glPopMatrix()
    
def handlePlayerMovement():
    global movement_keys_pressed, player_acceleration, player_forward_velocity_multiplier, player_sideward_velocity_multiplier
    global player_pos, world_ground_level, player_upward_velocity_multiplier

    player_movement_vector_x, player_movement_vector_y = get_player_forward_vector()

    key_pressed = False

    if movement_keys_pressed['w']:
        key_pressed = True
        player_forward_velocity_multiplier = min(player_forward_velocity_multiplier + player_acceleration * delta_time, 1)


    if movement_keys_pressed['s']:
        key_pressed = True
        player_forward_velocity_multiplier = max(player_forward_velocity_multiplier - player_acceleration * delta_time, -1)

    if movement_keys_pressed['a']:
        key_pressed = True
        player_sideward_velocity_multiplier = min(player_sideward_velocity_multiplier + player_acceleration * delta_time, 1)

    if movement_keys_pressed['d']:
        key_pressed = True
        player_sideward_velocity_multiplier = max(player_sideward_velocity_multiplier - player_acceleration * delta_time, -1)

    if movement_keys_pressed['space'] and is_player_grounded():
        player_upward_velocity_multiplier = player_jump_force
    #deceleraton
    if not key_pressed:

        if player_forward_velocity_multiplier < 0:
            player_forward_velocity_multiplier += player_acceleration * delta_time
            if player_forward_velocity_multiplier > 0: 
                player_forward_velocity_multiplier = 0

        elif player_forward_velocity_multiplier > 0:
            player_forward_velocity_multiplier -= player_acceleration * delta_time
            if player_forward_velocity_multiplier < 0:
                player_forward_velocity_multiplier = 0

        if player_sideward_velocity_multiplier < 0:
            player_sideward_velocity_multiplier += player_acceleration * delta_time
            if player_sideward_velocity_multiplier > 0: 
                player_sideward_velocity_multiplier = 0

        elif player_sideward_velocity_multiplier > 0:
            player_sideward_velocity_multiplier -= player_acceleration * delta_time
            if player_sideward_velocity_multiplier < 0:
                player_sideward_velocity_multiplier = 0

    #forward_movement
    movement_vector_x = player_normal_movement_velocity * player_movement_vector_x * delta_time * player_forward_velocity_multiplier
    movement_vector_y = player_normal_movement_velocity * player_movement_vector_y * delta_time * player_forward_velocity_multiplier
    movement_vector_z = 0
    move_player(movement_vector_x, movement_vector_y, movement_vector_z)

    
    #sideways_movement
    left_movement_vector_x = - player_movement_vector_y * player_normal_movement_velocity * delta_time * player_sideward_velocity_multiplier
    left_movement_vector_y = player_movement_vector_x * player_normal_movement_velocity * delta_time * player_sideward_velocity_multiplier
    move_player(left_movement_vector_x, left_movement_vector_y , 0)

    #gravity
    if not is_player_grounded():
        player_upward_velocity_multiplier -= player_gravity * delta_time
        if player_pos[2] - player_height < world_ground_level:
            player_pos[2] = world_ground_level + player_height

    if is_player_grounded() and player_upward_velocity_multiplier < 0:
        player_upward_velocity_multiplier = 0

    move_player(0, 0, 9 * player_upward_velocity_multiplier * delta_time)


def keyboardListener(key, x, y):
    """
    Handles keyboard inputs for player movement, gun rotation, camera updates, and cheat mode toggles.
    """
    global player_pos, camera_mode, cursor_locked, movement_keys_pressed

    player_movement_vector_x, player_movement_vector_y = get_player_forward_vector()



    if key == b'\x1b':  # ESC
        cursor_locked = not cursor_locked
        if not cursor_locked:
            glutSetCursor(GLUT_CURSOR_LEFT_ARROW)
        else:
            glutSetCursor(GLUT_CURSOR_NONE)
            glutWarpPointer(mouse_center_x, mouse_center_y)

    if key == b'w':
        movement_keys_pressed['w'] = True
    if key == b's':
        movement_keys_pressed['s'] = True
    if key == b'a':
        movement_keys_pressed['a'] = True
    if key == b'd':
        movement_keys_pressed['d'] = True

    if key == b' ':
        movement_keys_pressed['space'] = True
    # # Toggle cheat mode (C key)
    # if key == b'c':

    if key == b'v':
        if camera_mode == 'tps':
            camera_mode = 'fps'
        else: 
            camera_mode = 'tps'

    # # Reset the game if R key is pressed
    # if key == b'r':

def keyboardUpListener(key, x, y):
    if key == b'w':
        movement_keys_pressed['w'] = False

    if key == b's':
        movement_keys_pressed['s'] = False

    if key == b'a':
        movement_keys_pressed['a'] = False

    if key == b'd':
        movement_keys_pressed['d'] = False
    if key == b' ':
        movement_keys_pressed['space'] = False

def mouseMotionListener(x, y):
    global camera_pitch, player_angle
    global last_mouse_x, last_mouse_y
    global mouse_sensitivity

    dy = y - mouse_center_y
    dx = x - mouse_center_x

    if not delta_time == None and cursor_locked: 
        camera_pitch -= dy * mouse_sensitivity * 0.5 * (delta_time * 10)
        player_angle -= dx * mouse_sensitivity * (delta_time * 17)


    # Prevent looking too far up/down
    if camera_pitch < -60:
        camera_pitch = -60
    elif camera_pitch > 60:
        camera_pitch = 60

    if cursor_locked:
        glutWarpPointer(mouse_center_x, mouse_center_y)
        


def specialKeyListener(key, x, y):
    """
    Handles special key inputs (arrow keys) for adjusting the camera angle and height.
    """
    # Move camera up (UP arrow key)
    # if key == GLUT_KEY_UP:

    # # Move camera down (DOWN arrow key)
    # if key == GLUT_KEY_DOWN:

    # moving camera left (LEFT arrow key)
    if key == GLUT_KEY_LEFT:
        pass

    # moving camera right (RIGHT arrow key)
    if key == GLUT_KEY_RIGHT:
        pass

def mouseListener(button, state, x, y):
    """
    Handles mouse inputs for firing bullets (left click) and toggling camera mode (right click).
    """
    # Left mouse button fires a bullet
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        shoot_bullet()

        # # Right mouse button toggles camera tracking mode
        # if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:


def setupCamera():
    """
    Configures the camera's projection and view settings.
    Uses a perspective projection and positions the camera to look at the target.
    """
    global weapon_bullet_ray_origin_pos

    glMatrixMode(GL_PROJECTION)  # Switch to projection matrix mode
    glLoadIdentity()  # Reset the projection matrix
    # Set up a perspective projection (field of view, aspect ratio, near clip, far clip)
    gluPerspective(fovY, window_width/ window_height, 0.1, 1500) # Think why aspect ration is 1.25?
    glMatrixMode(GL_MODELVIEW)  # Switch to model-view matrix mode
    glLoadIdentity()  # Reset the model-view matrix

    player_x, player_y, player_z = player_pos
    player_forward_vector_x ,player_forward_vector_y = get_player_forward_vector()
    player_aim_vector_x, player_aim_vector_y, player_aim_vector_z = get_player_aim_vector() 
    if camera_mode == 'fps':
        camera_pos_offset = 0
        camera_lookAt_offset = 200
        camera_pos_x = player_x + camera_pos_offset * player_forward_vector_x
        camera_pos_y = player_y + camera_pos_offset * player_forward_vector_y
        camera_pos_z = player_z + 50
        weapon_bullet_ray_origin_pos = [camera_pos_x, camera_pos_y, camera_pos_z]

    if camera_mode == 'tps':
        camera_pos_offset = - 75
        camera_lookAt_offset = 200
        camera_pos_x = player_x + camera_pos_offset * player_forward_vector_x
        camera_pos_y = player_y + camera_pos_offset * player_forward_vector_y
        camera_pos_z = player_z + 70
        weapon_bullet_ray_origin_pos = [camera_pos_x, camera_pos_y, camera_pos_z]

    camera_look_at_x = player_x + camera_lookAt_offset * player_aim_vector_x
    camera_look_at_y = player_y + camera_lookAt_offset * player_aim_vector_y
    camera_look_at_z = player_z + 50 + camera_lookAt_offset * player_aim_vector_z
    # Position the camera and set its orientation
    gluLookAt(camera_pos_x, camera_pos_y , camera_pos_z,  # Camera position
              camera_look_at_x, camera_look_at_y, camera_look_at_z,  # Look-at target
              0, 0, 1)  # Up vector (z-axis)

def get_crosshair_target():
    aim_x, aim_y, aim_z = get_player_aim_vector()

    ray_origin_x, ray_origin_y, ray_origin_z = weapon_bullet_ray_origin_pos
    aim_distance = 500

    target_x = ray_origin_x + aim_x * aim_distance
    target_y = ray_origin_y + aim_y * aim_distance
    target_z = ray_origin_z + aim_z * aim_distance

    return (target_x, target_y, target_z)

def shoot_bullet():
    global bullets
    target_x, target_y, target_z = get_crosshair_target()

    muzzle_x, muzzle_y, muzzle_z = weapon_muzzle_pos

    direction_x = target_x - muzzle_x
    direction_y = target_y - muzzle_y
    direction_z = target_z - muzzle_z

    length = (direction_x ** 2 +direction_y ** 2 +direction_z ** 2) ** 0.5

    direction_x /= length
    direction_y /= length
    direction_z /= length

    bullet = {'pos': [muzzle_x, muzzle_y, muzzle_z], 'direction': [direction_x, direction_y, direction_z], 'speed' : 10}

    bullets.append(bullet)

def move_bullets():

    global bullets
    for bullet in bullets:

        bullet['pos'][0] += bullet['direction'][0] * bullet['speed'] * delta_time * 100
        bullet['pos'][1] += bullet['direction'][1] * bullet['speed'] * delta_time * 100
        bullet['pos'][2] += bullet['direction'][2] * bullet['speed'] * delta_time * 100

def draw_bullets():

    for bullet in bullets:
        x, y, z = bullet['pos']
        if should_illuminated_objected_be_rendered((x,y,z)):

            glPushMatrix()
            glColor3f(1, 1, 0)
            glTranslatef(x, y, z)
            glutSolidSphere(5, 10, 10)
            glPopMatrix()

def updateWeaponMuzzlePosition():
    global player_pos, weapon_muzzle_pos
    weapon_lenth = 80
    weapon_side_offset = -50
    player_forward_x, player_forward_y = get_player_forward_vector()
    muzzle_x = player_pos[0] + player_forward_x * weapon_lenth
    muzzle_y = player_pos[1] + player_forward_y * weapon_lenth

    player_perpendicular_x = player_forward_y
    player_perpendicular_y = - player_forward_x
    muzzle_x += player_perpendicular_x * weapon_side_offset
    muzzle_y += player_perpendicular_y * weapon_side_offset

    muzzle_z = player_pos[2] - player_height / 2

    weapon_muzzle_pos = [muzzle_x, muzzle_y, muzzle_z]

def idle():
    """
    Idle function that runs continuously:
    - Triggers screen redraw for real-time updates.
    """
    global current_time, delta_time
    new_time = time.time()
    delta_time = new_time - current_time
    current_time = new_time

    handlePlayerMovement()
    updateWeaponMuzzlePosition()
    move_bullets()
    # Ensure the screen updates with the latest changes
    glutPostRedisplay()


def showScreen():
    """
    Display function to render the game scene:
    - Clears the screen and sets up the camera.
    - Draws everything of the screen
    """
    # Clear color and depth buffers
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()  # Reset modelview matrix
    glViewport(0, 0, window_width, window_height)  # Set viewport size

    setupCamera()  # Configure camera perspective

    render_tiles()
    drawPlayer()
    draw_bullets()

    # Display game info text at a fixed screen position
    draw_text(10, 770, f"A Random Fixed Position Text")
    draw_text(10, 740, f"See how the position and variable change?: {'meow'}")
    drawCrosshair()
    # Swap buffers for smooth rendering (double buffering)
    glutSwapBuffers()


# Main function to set up OpenGL window and loop
def main():

    loadMap()

    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)  # Double buffering, RGB color, depth test
    glutInitWindowSize(window_width, window_height)  # Window size
    glutInitWindowPosition(0, 0)  # Window position
    wind = glutCreateWindow(b"3D OpenGL Intro")  # Create the window

    glEnable(GL_DEPTH_TEST)

    global cursor_locked
    cursor_locked = True
    glutWarpPointer(mouse_center_x, mouse_center_y)
    glutSetCursor(GLUT_CURSOR_NONE)



    glutDisplayFunc(showScreen)  # Register display function
    glutKeyboardFunc(keyboardListener)  # Register keyboard listener
    glutKeyboardUpFunc(keyboardUpListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutPassiveMotionFunc(mouseMotionListener)
    glutIdleFunc(idle)  # Register the idle function to move the bullet automatically

    glutMainLoop()  # Enter the GLUT main loop

if __name__ == "__main__":
    main()