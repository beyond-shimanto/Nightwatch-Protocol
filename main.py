from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import time
import math

# Camera-related variables
camera_mode = 'tps'
fovY = 75  # Field of view
camera_pitch = 0


last_mouse_x = 500
last_mouse_y = 400
mouse_sensitivity = 0.4

current_time = time.time()
delta_time = None

player_pos = [0,0,0]
player_angle = 0

player_normal_movement_velocity = 200
player_accelarated_movement_velocity = 100

grid_dimension = (100,100)
grid_tile_length = 10
grid_tile_res = 1
grid_color = [0.2,0.4,0.4]
wall_cubeoid_res = 2
flashlight_tiles_radius = 25
flashlight_radius = grid_tile_length * flashlight_tiles_radius
flashlight_radius_squared = flashlight_radius ** 2

walls = [[5,90,50,2.5, 75, (0,1,0)],
         [40,42.5,55,2.5, 75, (0,1,0)],
         [5,5,50,2.5, 75, (0,1,0)],
         [10,50,2.5,25, 75, (0,1,0)],
         [55,70,25,10, 30, (0,1,0)]]

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
    brightness_value = (flashlight_radius_squared - distance_from_player_squared) / (flashlight_radius_squared + 2* distance_from_player_squared)
    return (preferred_color[0] * brightness_value, preferred_color[1] * brightness_value, preferred_color[2] * brightness_value)

def should_objected_be_rendered(object_pos):
    object_distance_from_player_squared = get_distance_squared(player_pos, object_pos)
    return object_distance_from_player_squared < flashlight_radius_squared

def get_object_color_brightness(distance_squared_from_player):
    # return 1
    res = (flashlight_radius_squared - distance_squared_from_player) / (flashlight_radius_squared + 2* distance_squared_from_player)
    return res

def get_brightness_adjusted_color(original_color, brightness):
    return (original_color[0] * brightness, original_color[1] * brightness, original_color[2] * brightness)

def drawCrosshair():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glColor3f(1, 1, 1)

    glBegin(GL_LINES)

    # Horizontal
    glVertex2f(490, 400)
    glVertex2f(510, 400)

    # Vertical
    glVertex2f(500, 390)
    glVertex2f(500, 410)

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

def drawWall(tile_x1, tile_y1, total_x_tiles, total_y_tiles, height, wall_color):
    init_x = (- grid_tile_length * grid_dimension[0]/ 2) + grid_tile_length * tile_x1
    init_y = (- grid_tile_length * grid_dimension[1] / 2) + grid_tile_length * tile_y1

    end_x = init_x + total_x_tiles * grid_tile_length
    end_y = init_y + total_y_tiles * grid_tile_length


    cuboid_length = grid_tile_length / wall_cubeoid_res
    total_stacked_cuboid = int(height / cuboid_length)

    player_x, player_y, player_z = player_pos

    cur_y = init_y
    cur_x = init_x

    while cur_y < end_y:
        cur_z = cuboid_length / 2
        for _ in range(total_stacked_cuboid):
            if should_objected_be_rendered((cur_x + cuboid_length/2, cur_y + cuboid_length/2, cur_z + cuboid_length/2)):
                cube_color = wall_color
                cube_color = get_adjusted_object_color((cur_x + cuboid_length/2, cur_y + cuboid_length/2, cur_z + cuboid_length/2), cube_color)
                glPushMatrix()
                glColor3f(cube_color[0], cube_color[1], cube_color[2])
                glTranslatef(cur_x + cuboid_length / 2, cur_y +  cuboid_length / 2, cur_z)  
                glutSolidCube(cuboid_length)
                glPopMatrix()

            cur_z += cuboid_length
        cur_y += cuboid_length

    cur_y = init_y
    cur_x = end_x - cuboid_length
    while cur_y < end_y:
        cur_z = cuboid_length / 2
        for _ in range(total_stacked_cuboid):
            if should_objected_be_rendered((cur_x + cuboid_length/2, cur_y + cuboid_length/2, cur_z + cuboid_length/2)):
                cube_color = wall_color
                cube_color = get_adjusted_object_color((cur_x + cuboid_length/2, cur_y + cuboid_length/2, cur_z + cuboid_length/2), cube_color)
                glPushMatrix()
                glColor3f(cube_color[0], cube_color[1], cube_color[2])
                glTranslatef(cur_x + cuboid_length / 2, cur_y +  cuboid_length / 2, cur_z)  
                glutSolidCube(cuboid_length)
                glPopMatrix()

            cur_z += cuboid_length
        cur_y += cuboid_length

    cur_x = init_x
    cur_y = init_y
    while cur_x < end_x:
        cur_z = cuboid_length / 2
        for _ in range(total_stacked_cuboid):
            if should_objected_be_rendered((cur_x + cuboid_length/2, cur_y + cuboid_length/2, cur_z + cuboid_length/2)):
                cube_color = wall_color
                cube_color = get_adjusted_object_color((cur_x + cuboid_length/2, cur_y + cuboid_length/2, cur_z + cuboid_length/2), cube_color)
                glPushMatrix()
                glColor3f(cube_color[0], cube_color[1], cube_color[2])
                glTranslatef(cur_x + cuboid_length / 2, cur_y +  cuboid_length / 2, cur_z)  
                glutSolidCube(cuboid_length)
                glPopMatrix()

            cur_z += cuboid_length
        cur_x += cuboid_length

    cur_x = init_x
    cur_y = end_y - cuboid_length
    while cur_x < end_x:
        cur_z = cuboid_length / 2
        for _ in range(total_stacked_cuboid):
            if should_objected_be_rendered((cur_x + cuboid_length/2, cur_y + cuboid_length/2, cur_z + cuboid_length/2)):
                cube_color = wall_color
                cube_color = get_adjusted_object_color((cur_x + cuboid_length/2, cur_y + cuboid_length/2, cur_z + cuboid_length/2), cube_color)
                glPushMatrix()
                glColor3f(cube_color[0], cube_color[1], cube_color[2])
                glTranslatef(cur_x + cuboid_length / 2, cur_y +  cuboid_length / 2, cur_z)  
                glutSolidCube(cuboid_length)
                glPopMatrix()

            cur_z += cuboid_length
        cur_x += cuboid_length


    cur_y = init_y
    while cur_y < end_y:
        cur_x = init_x

        while cur_x < end_x:

            ceiling_z = height + cuboid_length / 2


            if should_objected_be_rendered((cur_x + cuboid_length / 2,cur_y + cuboid_length / 2,ceiling_z)):

                cube_color = wall_color
                cube_color = get_adjusted_object_color((cur_x + cuboid_length / 2,cur_y + cuboid_length / 2,ceiling_z), cube_color)

                glPushMatrix()

                glColor3f(cube_color[0],cube_color[1],cube_color[2])

                glTranslatef(cur_x + cuboid_length / 2,cur_y + cuboid_length / 2,ceiling_z)

                glutSolidCube(cuboid_length)

                glPopMatrix()

            cur_x += cuboid_length

        cur_y += cuboid_length

def drawFloor():

    init_x = - (grid_tile_length * grid_dimension[0]) / 2
    init_y = - (grid_tile_length * grid_dimension[1]) / 2

    end_x = (grid_tile_length * grid_dimension[0]) / 2
    end_y = (grid_tile_length * grid_dimension[1]) / 2


    tileoid_length = grid_tile_length / grid_tile_res

    cur_y = init_y



    while (cur_y < end_y):
        cur_x = init_x

        while(cur_x < end_x):

            cur_tile_mid_x = cur_x + grid_tile_length / 2
            cur_tile_mid_y = cur_y + grid_tile_length / 2

            player_x, player_y, player_z = player_pos

            if should_objected_be_rendered((cur_tile_mid_x, cur_tile_mid_y, 0)):
                tile_color_brightness_adjusted = get_adjusted_object_color((cur_tile_mid_x, cur_tile_mid_y, 0), grid_color)
                glPushMatrix()
                glColor3f(tile_color_brightness_adjusted[0], tile_color_brightness_adjusted[1] , tile_color_brightness_adjusted[2])
                glTranslatef(cur_x + tileoid_length / 2, cur_y + tileoid_length/2, -1)
                glScale(tileoid_length, tileoid_length, 2)
                glutSolidCube(1)
                glPopMatrix()

                
            
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
    

def keyboardListener(key, x, y):
    """
    Handles keyboard inputs for player movement, gun rotation, camera updates, and cheat mode toggles.
    """
    global player_pos, camera_mode

    player_movement_vector_x, player_movement_vector_y = get_player_forward_vector()

    if key == b'w':  
        player_pos[0] += player_normal_movement_velocity * player_movement_vector_x * delta_time
        player_pos[1] += player_normal_movement_velocity * player_movement_vector_y * delta_time



    if key == b's':
        player_pos[0] -= player_normal_movement_velocity * player_movement_vector_x * delta_time
        player_pos[1] -= player_normal_movement_velocity * player_movement_vector_y * delta_time

    if key == b'a':
        left_movement_vector_x = - player_movement_vector_y
        left_movement_vector_y = player_movement_vector_x
        player_pos[0] += player_normal_movement_velocity * left_movement_vector_x * delta_time
        player_pos[1] += player_normal_movement_velocity * left_movement_vector_y * delta_time


    if key == b'd':
        right_movement_vector_x = player_movement_vector_y
        right_movement_vector_y = - player_movement_vector_x
        player_pos[0] += player_normal_movement_velocity * right_movement_vector_x * delta_time
        player_pos[1] += player_normal_movement_velocity * right_movement_vector_y * delta_time

    # # Toggle cheat mode (C key)
    # if key == b'c':

    if key == b'v':
        if camera_mode == 'tps':
            camera_mode = 'fps'
        else: 
            camera_mode = 'tps'

    # # Reset the game if R key is pressed
    # if key == b'r':

def mouseMotionListener(x, y):
    global camera_pitch, player_angle
    global last_mouse_x, last_mouse_y
    global mouse_sensitivity

    dy = y - last_mouse_y
    dx = x - last_mouse_x

    if not delta_time == None: 
        camera_pitch -= dy * mouse_sensitivity * 0.5 * (delta_time * 10)
        player_angle -= dx * mouse_sensitivity * (delta_time * 17)


    # Prevent looking too far up/down
    if camera_pitch < -60:
        camera_pitch = -60
    elif camera_pitch > 60:
        camera_pitch = 60

    last_mouse_x = x
    last_mouse_y = y


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
        # # Left mouse button fires a bullet
        # if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:

        # # Right mouse button toggles camera tracking mode
        # if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:


def setupCamera():
    """
    Configures the camera's projection and view settings.
    Uses a perspective projection and positions the camera to look at the target.
    """
    glMatrixMode(GL_PROJECTION)  # Switch to projection matrix mode
    glLoadIdentity()  # Reset the projection matrix
    # Set up a perspective projection (field of view, aspect ratio, near clip, far clip)
    gluPerspective(fovY, 1.25, 0.1, 1500) # Think why aspect ration is 1.25?
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

    if camera_mode == 'tps':
        camera_pos_offset = - 75
        camera_lookAt_offset = 200
        camera_pos_x = player_x + camera_pos_offset * player_forward_vector_x
        camera_pos_y = player_y + camera_pos_offset * player_forward_vector_y
        camera_pos_z = player_z + 70

    camera_look_at_x = player_x + camera_lookAt_offset * player_aim_vector_x
    camera_look_at_y = player_y + camera_lookAt_offset * player_aim_vector_y
    camera_look_at_z = player_z + 50 + camera_lookAt_offset * player_aim_vector_z
    # Position the camera and set its orientation
    gluLookAt(camera_pos_x, camera_pos_y , camera_pos_z,  # Camera position
              camera_look_at_x, camera_look_at_y, camera_look_at_z,  # Look-at target
              0, 0, 1)  # Up vector (z-axis)


def idle():
    """
    Idle function that runs continuously:
    - Triggers screen redraw for real-time updates.
    """
    global current_time, delta_time
    new_time = time.time()
    delta_time = new_time - current_time
    current_time = new_time

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
    glViewport(0, 0, 1000, 800)  # Set viewport size

    setupCamera()  # Configure camera perspective

    drawFloor()
    drawPlayer()

    for wall in walls:
        wall_start_x, wall_start_y, wall_length_x_tiles, wall_length_y_tiles, wall_height, wall_color = wall
        drawWall(wall_start_x, wall_start_y, wall_length_x_tiles, wall_length_y_tiles, wall_height, wall_color)

    # Display game info text at a fixed screen position
    draw_text(10, 770, f"A Random Fixed Position Text")
    draw_text(10, 740, f"See how the position and variable change?: {'meow'}")
    drawCrosshair()
    # Swap buffers for smooth rendering (double buffering)
    glutSwapBuffers()


# Main function to set up OpenGL window and loop
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)  # Double buffering, RGB color, depth test
    glutInitWindowSize(1000, 800)  # Window size
    glutInitWindowPosition(0, 0)  # Window position
    wind = glutCreateWindow(b"3D OpenGL Intro")  # Create the window

    glEnable(GL_DEPTH_TEST)
    glutSetCursor(GLUT_CURSOR_NONE)
    glutWarpPointer(500,400)

    glutDisplayFunc(showScreen)  # Register display function
    glutKeyboardFunc(keyboardListener)  # Register keyboard listener
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutPassiveMotionFunc(mouseMotionListener)
    glutIdleFunc(idle)  # Register the idle function to move the bullet automatically

    glutMainLoop()  # Enter the GLUT main loop

if __name__ == "__main__":
    main()