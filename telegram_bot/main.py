import asyncio
import os
import pickle
import random
from pathlib import Path
from typing import Any, Tuple, Optional, Sequence

from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.scene import SceneRegistry, ScenesManager, Scene, on
from aiogram.fsm.storage.memory import SimpleEventIsolation
from aiogram.types import Message, ReplyKeyboardRemove

CITIES = pickle.load((Path(__file__).parent / "cities.pickle").open(mode='rb'))


class QuizScene(Scene, state="quiz"):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _fetch_random_city_with_first_letter(
            self,
            used_cities: Sequence[str],
            letter: Optional[str] = '',
            ) -> Tuple[str, str]:
        assert len(letter) <= 1
        cities = [c for c in CITIES.keys() if c.startswith(letter.upper()) and c not in used_cities]
        if not cities:
            raise OutOfCities()
        choice = random.choice(cities)
        return choice

    @on.message.enter()
    async def on_enter(self, message: Message, state: FSMContext, first_letter: str = '') -> Any:
        if not first_letter:
            await state.set_data({'used': []})
            await message.answer("Let's begin the capitals game!")
        current_data = await state.get_data()
        used_cities = current_data['used']
        try:
            capital = self._fetch_random_city_with_first_letter(
                used_cities,
                first_letter,
                )
        except OutOfCities:
            await message.answer(f"No capitals starting with {first_letter} left, you won!")
            return await self.wizard.exit()
        new_used_cities = [*used_cities, capital]
        await state.set_data({'letter': capital[-1], 'used': new_used_cities})
        try:
            self._fetch_random_city_with_first_letter(new_used_cities, capital[-1])
        except OutOfCities:
            await message.answer(
                f"Hahahaha! I won, I am machine! "
                f"My choice is {capital}, no capital starting with {capital[-1]}!")
        else:
            await message.reply(
                f"I say: {capital}, that's the capital of {CITIES[capital]}.\n"
                f"Your turn: give me a capital that starts with \"{capital[-1]}\"!")

    @on.message(F.text)
    async def answer(self, message: Message, state: FSMContext) -> None:
        user_answer = message.text.strip()
        data = await state.get_data()
        expected_letter = data['letter']
        current_data = await state.get_data()
        used_cities = current_data['used']
        if not user_answer.lower().startswith(expected_letter):
            await message.reply(f"Please enter a capital starting with letter {expected_letter}.")
        elif not user_answer.lower() in [c.lower().strip() for c in CITIES.keys()]:
            await message.reply(f"Please enter a correct capital.")
        elif user_answer.lower() in [c.lower().strip() for c in used_cities]:
            await message.reply(f"Already used capital. Please enter another one.")
        else:
            await state.set_data({'letter': user_answer[-1], 'used': [*used_cities, user_answer]})
            await self.wizard.retake(first_letter=user_answer[-1])


quiz_router = Router(name=__name__)
quiz_router.message.register(QuizScene.as_handler(), Command("quiz"))


@quiz_router.message(Command("start"))
async def command_start(message: Message, scenes: ScenesManager):
    await scenes.close()
    await message.answer(
        "Hi! This is a quiz bot. To start the quiz, use the /quiz command.",
        reply_markup=ReplyKeyboardRemove(),
    )


def create_dispatcher():
    dispatcher = Dispatcher(events_isolation=SimpleEventIsolation())
    dispatcher.include_router(quiz_router)
    scene_registry = SceneRegistry(dispatcher)
    scene_registry.add(QuizScene)
    return dispatcher


class OutOfCities(Exception):
    pass


async def main():
    bot_token = os.environ.get('BOT_TOKEN')
    bot = Bot(token=bot_token)
    dp = create_dispatcher()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
