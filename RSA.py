from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)


P, Q, D, TEXT = range(4)

def Euclid(a, b):
    output = []
    x = [a, b]
    p = [1, 0]
    q = [0, 1]
    y = ["-"]

    output.append("e находим по расширенному алгоритму Евклида")

    i = 1
    step = 1

    while True:

        y_i = x[i - 1] // x[i]
        output.append(f"y_{i+1} = x_{i-1} / x_{i} = {x[i-1]} / {x[i]} = {y_i}")

        x_i = x[i - 1] - y_i * x[i]
        output.append(
            f"x_{i+1} = x_{i-1} - y_{i+1}·x_{i} = "
            f"{x[i-1]} - {y_i}·{x[i]} = {x_i}"
        )

        x.append(x_i)
        y.append(y_i)

        if x_i == 0:
            p.append(" ")
            q.append(" ")
            break

        p_i = p[i - 1] - p[i] * y_i
        output.append(
            f"p_{i+1} = p_{i-1} - y_{i+1}·p_{i} = "
            f"{p[i-1]} - {y_i}·{p[i]} = {p_i}"
        )

        q_i = q[i - 1] - q[i] * y_i
        output.append(
            f"q_{i+1} = q_{i-1} - y_{i+1}·q_{i} = "
            f"{q[i-1]} - {y_i}·{q[i]} = {q_i}"
        )

        p.append(p_i)
        q.append(q_i)

        i += 1
        step += 1

    output.append("Таблица:")

    rows = [
        ["i"] + [str(j) for j in range(len(x))],
        ["x"] + list(map(str, x)),
        ["y"] + list(map(str, y)),
        ["p"] + list(map(str, p)),
        ["q"] + list(map(str, q)),
    ]

    max_cols = max(len(row) for row in rows)

    for row in rows:
        while len(row) < max_cols:
            row.append("")

    col_widths = []
    for col in range(max_cols):
        max_len = max(len(row[col]) for row in rows)
        col_widths.append(max_len + 2)

    table_lines = []
    for row in rows:
        line = ""
        for i, cell in enumerate(row):
            line += cell.ljust(col_widths[i])
        table_lines.append(line)
    output.extend(table_lines)

    gcd_index = len(x) - 2
    gcd = x[gcd_index]
    p_coef = p[gcd_index]
    q_coef = q[gcd_index]

    return gcd, p_coef, q_coef, "\n".join(output)


def is_prime(num):
    if num < 2:
        return False
    for i in range(2, int(num ** 0.5) + 1):
        if num % i == 0:
            return False
    return True


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите простое число p (Закрытый ключ): ")
    return P


async def get_p(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.text.isdigit():
        await update.message.reply_text("Ошибка: введите целое число p.")
        return P

    p = int(update.message.text)

    if not is_prime(p):
        await update.message.reply_text("Ошибка: p должно быть простым числом.")
        return P

    context.user_data["p"] = p
    await update.message.reply_text("Введите простое число q (Закрытый ключ): ")
    return Q


async def get_q(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.text.isdigit():
        await update.message.reply_text("Ошибка: введите целое число q.")
        return Q

    q = int(update.message.text)

    if not is_prime(q):
        await update.message.reply_text("Ошибка: q должно быть простым числом.")
        return Q

    if q == context.user_data["p"]:
        await update.message.reply_text("Ошибка: p и q должны быть различными.")
        return Q

    context.user_data["q"] = q
    await update.message.reply_text("Введите число d (Закрытый ключ): ")
    return D


async def get_d(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.text.isdigit():
        await update.message.reply_text("Ошибка: d должно быть целым числом.")
        return D

    d = int(update.message.text)

    if d <= 0:
        await update.message.reply_text("Ошибка: d должно быть положительным.")
        return D

    context.user_data["d"] = d
    await update.message.reply_text("Введите текст: ")
    return TEXT


async def process_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text.isdigit():
        await update.message.reply_text("Ошибка: здесь нужно ввести текст, а не число.")
        return TEXT
    p = context.user_data["p"]
    q = context.user_data["q"]
    d = context.user_data["d"]
    text = update.message.text.lower()

    output = []

    alphabet = [
        "а","б","в","г","д","е","ё","ж","з",
        "и","й","к","л","м","н","о","п",
        "р","с","т","у","ф","х","ц","ч",
        "ш","щ","ъ","ы","ь","э","ю","я"
    ]

    n = p * q
    output.append("\nВычисление n (открытый ключ):")
    output.append(f"n = p · q")
    output.append(f"n = {p} · {q} = {n}")

    output.append("\nВычисление функции Эйлера φ(n):")
    output.append("Так как p и q - простые числа, используется формула:")
    output.append("φ(n) = φ(p · q) = (p - 1)(q - 1)")

    phi = (p - 1) * (q - 1)
    output.append(f"φ(n) = ({p} - 1)({q} - 1) = {p-1} · {q-1} = {phi}")

    output.append("\ne · d ≡ 1 (mod φ(n)), где e - открытый ключ")
    gcd, p_coef, q_coef, euclid_output = Euclid(phi, d)
    output.append(euclid_output)

    if gcd != 1:
        output.append("Ошибка: d не взаимно просто с φ(n).")
        await update.message.reply_text("\n".join(output))
        return ConversationHandler.END

    output.append("Следовательно:")
    output.append(f"{d}·{q_coef} ≡ 1 (mod {phi})")

    output.append("\nПреобразование текста в числовую форму:")
    result = []

    for char in text:
        if char in alphabet:
            index = alphabet.index(char)
            result.append(str(index))
            output.append(f"{char} → {index}")
        else:
            output.append(f"{char} → пропуск (символ отсутствует в алфавите)")

    output.append("\nРезультат:")
    output.append(" ".join(result))

    e = q_coef % phi

    output.append("\nШифрование по формуле B = x^e mod n, где x - порядковый номер буквы")
    encrypted = []

    for char in text:
        if char in alphabet:
            x = alphabet.index(char)
            v = pow(x, e, n)
            encrypted.append(str(v))
            output.append(f"в({char})= {x}^{e} mod {n} = {v}")

    output.append("\nШТ:")
    cipher_letters = []

    for value in encrypted:
        num = int(value)
        letter = alphabet[num % len(alphabet)]
        cipher_letters.append(letter)
        output.append(f"{num} → {letter}")

    output.append("\nА получает ШТ:")
    output.append("\nДешифрование по формуле x = в^d mod n:")

    decrypted_indices = []
    decrypted_letters = []

    for cipher_letter, value in zip(cipher_letters, encrypted):
        v = int(value)
        x = pow(v, d, n)
        decrypted_indices.append(str(x))

        if 0 <= x < len(alphabet):
            letter = alphabet[x]
            decrypted_letters.append(letter)
            output.append(f"x({cipher_letter}) = {v}^{d} mod {n} = {x} → {letter}")
        else:
            output.append(f"x({cipher_letter}) = {v}^{d} mod {n} = {x} → вне диапазона алфавита")

    output.append("\nРасшифрованные индексы:")
    output.append(" ".join(decrypted_indices))

    output.append("\nРасшифрованный текст:")
    output.append("".join(decrypted_letters))

    text_to_send = "\n".join(output)
    print(len(text_to_send))
    text_to_send = "\n".join(output)

    MAX_LEN = 4000  

    for i in range(0, len(text_to_send), MAX_LEN):
        await update.message.reply_text(
            text_to_send[i:i + MAX_LEN],
            parse_mode=None
        )
    return ConversationHandler.END


def main():
    app = ApplicationBuilder().token("utoken").build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            P: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_p)],
            Q: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_q)],
            D: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_d)],
            TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_text)],
        },
        fallbacks=[],
    )

    app.add_handler(conv)
    app.run_polling()


if __name__ == "__main__":
    main()


