![Bluebook Logo](https://github.com/ilya-smut/blue-book/blob/main/bluebook/static/images/book.png)
# Blue Book
![Demo](https://github.com/ilya-smut/blue-book/blob/main/examples/videos/bluebook%20gif.gif)

Blue Book is an application that generates multiple-choice questions for CompTIA Security+ preparation at the press of a button. It uses the Gemini API to generate questions and provides instant feedback on answers.

## Features
- Generate CompTIA Security+ multiple-choice questions.
- Specify the topic you want to the questions to focus on.
- Submit answers and receive immediate feedback.
- Explanation of correct and incorrect answers to enhance learning.
- Can be run in a docker container with minimal setup

## Installation

You can install bluebook with pip:
   ```sh
   pip install student-bluebook
   ```

With pipx
   ```sh
   pipx install student-bluebook
   ```

Or you can simply run it in a docker container
   ```sh
   git clone https://github.com/ilya-smut/blue-book
   cd blue-book/
   docker compose up -d
   ```

## Usage

Please see bluebook's interface and capabilities on this wiki page [wiki page](https://github.com/ilya-smut/blue-book/wiki):

To start the application, use the following command:
```sh
bluebook start
```

## Contributing
If you’d like to contribute to Blue Book, feel free to submit a pull request or open an issue.

## License
This project is licensed under the GPLv3

## Contact
For any questions or feedback, feel free to reach out.

