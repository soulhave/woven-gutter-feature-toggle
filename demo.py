from gutter.client.testutils import switches

from gutter.client.operators.comparable import MoreThan

from gutter.client.models import Switch, Condition
from gutter.client import get_gutter_client
from gutter.client import arguments

PARENT_SWITCH_CHILD_2 = 'parent_switch_disabled:field_2'

PARENT_SWITCH_CHILD_1 = 'parent_switch_disabled:field_1'

PARENT_SWITCH = 'parent_switch_disabled'

SWITCH_DISABLED = 'simple_switch_disabled'

SIMPLE_SWITCH_DISABLED = 'auto_created_simple_switch_disabled'

SIMPLE_SWITCH_ENABLE = 'simple_switch_enable'

ENABLE_WITH_DESCRIPTION = 'simple_switch_enable_with_description'

ENABLE_WITH_CONDITIONAL = 'selective_switch_enable_with_conditional'

manager = get_gutter_client(
    storage={},
    autocreate=True
)


class User:
    """
    Users Business Entity
    """
    name: str
    age: int
    is_admin: bool

    def __init__(self, name: str, age: int = 0, is_admin: bool = False):
        self.name = name
        self.age = age
        self.is_admin = is_admin

    def __str__(self):
        return '<name: {}, age {}, is_admin {}>'\
            .format(self.name, self.age, self.is_admin)


class UserArgument(arguments.Container):
    """
    UserArguments Container. This is a class that translate
    the business entity to a knew structure for gutter.
    """

    # Generate compatibility with the business model.
    COMPATIBLE_TYPE = User

    name = arguments.String('name')
    age = arguments.Integer('age')
    is_admin = arguments.Boolean('is_admin')


def create_simple_switch_disabled():
    """
    Create a simple swith disabled and register it.
    :return: anything
    """
    switch = Switch(SWITCH_DISABLED)

    manager.register(
        switch
    )

    print_and_check_flag(switch, SWITCH_DISABLED)


def auto_create_simple_switch_disabled():
    """
    Auto create a simple switch disabled and register it.
    :return: anything
    """
    manager.active(SIMPLE_SWITCH_DISABLED)
    print_and_check_flag(manager.switch(SIMPLE_SWITCH_DISABLED),
                         SIMPLE_SWITCH_DISABLED)


def create_simple_switch_enable():
    """
    Create a simple switch enabled.
    :return:
    """
    switch = Switch(SIMPLE_SWITCH_ENABLE, state=Switch.states.GLOBAL)

    manager.register(
        switch
    )

    print_and_check_flag(switch, SIMPLE_SWITCH_ENABLE)


def create_simple_switch_enable_with_description():
    """
    Create a simple switch enabled with description.
    :return:
    """
    switch = Switch(ENABLE_WITH_DESCRIPTION,
                    state=Switch.states.GLOBAL,
                    description='Simple switch enabled with description \\o/')

    manager.register(
        switch
    )

    print_and_check_flag(switch, ENABLE_WITH_DESCRIPTION)


def create_selective_switch_enable_with_conditional():
    """
    Create a switch with type selective.
    :return:
    """
    _conditional_switch = Switch(
        ENABLE_WITH_CONDITIONAL,
        state=Switch.states.SELECTIVE
    )
    _conditional_switch.name
    _condition = Condition(
        argument=UserArgument,
        attribute='age',
        operator=MoreThan(lower_limit=50),
        # negative=True
    )

    _conditional_switch.conditions.append(
        _condition
    )

    manager.register(_conditional_switch)

    print_new_switch(_conditional_switch)

    ### Validate ###
    _users = [
        User('Alisson'),
        User('Fred', 40),
        User('Elisson', 70),
        User('Ulisses', 51)
    ]

    [print('--> {} :: {} :: {}'.format(
        ENABLE_WITH_CONDITIONAL,
        _u,
        manager.active(ENABLE_WITH_CONDITIONAL, _u)
    )) for _u in _users]


def create_switch_parent_and_child():
    """
    Heriarchical Switches, with children.
    :return:
    """
    _switches = [
        Switch(PARENT_SWITCH),
        # This one it will respect the parent status
        Switch(PARENT_SWITCH_CHILD_1, state=Switch.states.GLOBAL, concent=True),
        # It will return true even parent is disabled
        Switch(PARENT_SWITCH_CHILD_2, state=Switch.states.GLOBAL, concent=False)
    ]

    _ = [(manager.register(_switch), print_new_switch(_switch))
         for _switch in _switches]

    print_parent_switches(_switches, 'FALSE')

    manager.switch(PARENT_SWITCH).state = Switch.states.GLOBAL

    print('\n')

    print_parent_switches(_switches, 'TRUE')


def print_parent_switches(switches, active):
    """
    Print switches.
    :type switches:
    :type active:
    """
    [print('--> PARENT {} :: {} :: {} :: {}'.format(
        active,
        _s.name,
        _s,
        manager.active(_s.name)
    )) for _s in switches]


##
def print_new_switch(switch):
    """
    Just print the swich
    :param switch:
    :return:
    """
    print("\n-----------------\n{}\n-----------------\n".format(switch))


def print_and_check_flag(switch, flag):
    """
    Print the switch and use the flag to check
    if the switch is active
    :param switch:
    :param flag:
    :return:
    """
    print_new_switch(switch)
    print('--> {} :: {}'.format(flag,
                                manager.active(flag)))


def main():
    # SIMPLE_SWITCH_DISABLED
    create_simple_switch_disabled()

    # SIMPLE_SWITCH_ENABLE
    create_simple_switch_enable()

    # SIMPLE_SWITCH_DISABLED
    auto_create_simple_switch_disabled()

    # ENABLE_WITH_DESCRIPTION
    create_simple_switch_enable_with_description()

    # ENABLE_WITH_CONDITIONAL
    create_selective_switch_enable_with_conditional()

    # PARENT_SWITCH
    create_switch_parent_and_child()


if __name__ == '__main__':
    main()
