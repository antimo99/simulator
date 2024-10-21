from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution

from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    ld = LaunchDescription()

    #### Argument: urdf file location #####
    # We have two arguments for this. package and urdf file path relative to the package
    ld.add_action(DeclareLaunchArgument('urdf_package',
                                        default_value='panda_sim',
                                        description='The package where the robot description is located'))
    ld.add_action(DeclareLaunchArgument('urdf_package_path',
                                        default_value='urdf/panda.urdf.xacro',
                                        description='The path to the robot description relative to the package root'))
    ########################################

    #### Argument: .rviz config file location #####
    # Find the path of the package 'uclv_aipr_panda_sim'
    this_package = FindPackageShare('panda_sim')
    default_rviz_config_path = PathJoinSubstitution([this_package, 'launch', 'demo.rviz'])
    ld.add_action(DeclareLaunchArgument(name='rviz_config', default_value=default_rviz_config_path,
                                        description='Absolute path to rviz config file'))
    ##############################################


    ########### Argument: jsp_gui == joint_state_publisher_gui ##############
    # This is a boolean argument
    # true = run the joint_state_publisher_gui node
    # false = run the joint_state_publisher node (without gui)
    # The use of this argument is below..
    ld.add_action(DeclareLaunchArgument(name='jsp_gui', default_value='true', choices=['true', 'false'],
                                        description='Flag to enable joint_state_publisher_gui'))
    ################################################################################

    
    ######### Run the robot_state_publisher ##############################
    # Here we call the launch file urdf_launch/launch/description.launch.py
    # It runs the robot_state_publisher_node
    # Have a look in /opt/ros/humble/share/urdf_launch/launch/description.launch.py

    # Find the path of the package 'urdf_launch'
    urdf_launch_package = FindPackageShare('urdf_launch')
    # need to manually pass configuration in because of https://github.com/ros2/launch/issues/313
    ld.add_action(IncludeLaunchDescription(
        PathJoinSubstitution([urdf_launch_package, 'launch', 'description.launch.py']),
        launch_arguments={
            'urdf_package': LaunchConfiguration('urdf_package'),
            'urdf_package_path': LaunchConfiguration('urdf_package_path')}.items()
    ))
    #####################################################################



    ########## Run the joint_state_publisher ########################
    # Depending on gui parameter, either launch joint_state_publisher or joint_state_publisher_gui
    ld.add_action(Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        condition=UnlessCondition(LaunchConfiguration('jsp_gui')),
        parameters=[
            {'source_list': ['cmd/joint_position']}
        ]
    ))

    ld.add_action(Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        condition=IfCondition(LaunchConfiguration('jsp_gui')),
        parameters=[
            {'source_list': ['cmd/joint_position']}
        ]
    ))
    ################################################################

    ######## Run rviz ##############################################
    ld.add_action(Node(
        package='rviz2',
        executable='rviz2',
        output='screen',
        arguments=['-d', LaunchConfiguration('rviz_config')],
    ))
    ###############################################################

    return ld
