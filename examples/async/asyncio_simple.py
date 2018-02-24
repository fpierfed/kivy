'''Example shows the recommended way of how to run Kivy with a asyncio
event loop as just another async coroutine.
'''
import asyncio
from concurrent.futures import CancelledError
import os

os.environ['KIVY_EVENTLOOP'] = 'asyncio'
'''asyncio needs to be set so that it'll be used for the event loop. '''

from kivy.app import async_runTouchApp                              # noqa
from kivy.lang.builder import Builder                               # noqa

kv = '''
BoxLayout:
    orientation: 'vertical'
    Button:
        id: btn
        text: 'Press me'
    BoxLayout:
        Label:
            id: label
'''


async def watch_button_closely(root):
    '''This is run side by side with the app and it watches and reacts to the
    button shown in kivy.'''
    label = root.ids.label
    i = 0

    # we watch for 7 button presses and then exit this task. if the app is
    # closed before that, run_app_happily will cancel all the tasks, so we
    # should catch it first and print it and then re-raise
    try:
        # watch the on_release event of the button and react to every release
        async for _ in root.ids.btn.async_bind('on_release'):       # noqa
            label.text = 'Pressed x{}'.format(i)
            if i == 7:
                break
            i += 1

        label.text = 'Goodbye :('
    except CancelledError:
        print('update_label1 canceled early')
    finally:
        print('Done with update_label1')


async def run_app_happily(root):
    '''This method, which runs Kivy, is run by asyncio as one of the coroutines.
    '''
    await async_runTouchApp(root)  # run Kivy
    print('App done')
    # now cancel all the other tasks that may be running
    for task in [t for t in asyncio.Task.all_tasks()
                 if t is not asyncio.Task.current_task()]:
        task.cancel()


async def waste_time_freely():
    '''This method is also run by asyncio and periodically prints something.'''
    try:
        while True:
            print('Sitting on the beach')
            await asyncio.sleep(2)
    finally:
        # when canceled, print that it finished
        print('Done wasting time')


async def main():
    root = Builder.load_string(kv)  # root widget
    await asyncio.wait([
        run_app_happily(root),
        watch_button_closely(root),
        waste_time_freely(),
    ])


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except CancelledError:
        print('All done.')
    loop.close()
