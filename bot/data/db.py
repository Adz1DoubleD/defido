import mysql.connector
import os


def create_connection():
    return mysql.connector.connect(
        host = os.getenv("DB_HOST"),
        user = os.getenv("DB_USER"),
        password = os.getenv("DB_PASSWORD"),
        database = os.getenv("DB_NAME") ,
        port = os.getenv("DB_PORT")
    )


def close_connection(connection, cursor):
    cursor.close()
    connection.close()


def filter_add(word, reply):
    try:
        connection = create_connection()
        cursor = connection.cursor()

        add_filter_query = """
        INSERT INTO filters (word, reply)
        VALUES (%s, %s);
        """

        filter_data = (word, reply)

        cursor.execute(add_filter_query, filter_data)
        connection.commit()

        close_connection(connection, cursor)

        return "Filter added successfully"
    except mysql.connector.Error as e:
        return f"Error: {e}"


def filter_delete(word):
    try:
        connection = create_connection()
        cursor = connection.cursor()

        delete_filter_query = """
        DELETE FROM filters
        WHERE word = %s;
        """

        filter_data = (word,)

        cursor.execute(delete_filter_query, filter_data)
        connection.commit()

        close_connection(connection, cursor)

        return "Filter deleted successfully"
    except mysql.connector.Error as e:
        return f"Error: {e}"


def filter_check(word):
    try:
        connection = create_connection()
        cursor = connection.cursor()

        select_filter_query = """
        SELECT reply FROM filters
        WHERE word = %s;
        """

        cursor.execute(select_filter_query, (word,))
        result = cursor.fetchone()

        close_connection(connection, cursor)

        return result[0] if result else None
    
    except mysql.connector.Error as e:
        return None


def filters_get() -> None:
    try:
        connection = create_connection()
        cursor = connection.cursor()

        select_all_words_query = """
        SELECT word FROM filters;
        """

        cursor.execute(select_all_words_query)
        words = cursor.fetchall()

        close_connection(connection, cursor)

        if words:
            word_list = [word[0] for word in words]
            word_list_str = "\n".join(word_list)
            return word_list_str
        

        else:
            return None
        
    except mysql.connector.Error as e:

        return None


def blacklist_check(message_text):
    try:
        connection = create_connection()
        cursor = connection.cursor()

        select_blacklist_query = """
        SELECT word FROM blacklist;
        """

        cursor.execute(select_blacklist_query)
        blacklisted_words = cursor.fetchall()

        for word in blacklisted_words:
            if word[0].lower() in message_text.lower():
                return True

        return False

    except mysql.connector.Error as e:
        print(f"Error: {e}")
        return False
    finally:
        close_connection(connection, cursor)


def blacklist_add(word):
    try:
        connection = create_connection()
        cursor = connection.cursor()

        add_to_blacklist_query = """
        INSERT INTO blacklist (word)
        VALUES (%s);
        """

        cursor.execute(add_to_blacklist_query, (word,))
        connection.commit()

    except mysql.connector.Error as e:
        print(f"Error: {e}")
    finally:
        close_connection(connection, cursor)


def blacklist_delete(word):
    try:
        connection = create_connection()
        cursor = connection.cursor()

        remove_from_blacklist_query = """
        DELETE FROM blacklist
        WHERE word = %s;
        """

        cursor.execute(remove_from_blacklist_query, (word,))
        connection.commit()

    except mysql.connector.Error as e:
        print(f"Error: {e}")
    finally:
        close_connection(connection, cursor)


def blacklist_get(word):
    try:
        connection = create_connection()
        cursor = connection.cursor()

        select_blacklist_query = """
        SELECT word FROM blacklist;
        """

        cursor.execute(select_blacklist_query)
        blacklisted_words = cursor.fetchall()

        return any(word.lower() == w[0].lower() for w in blacklisted_words)

    except mysql.connector.Error as e:
        print(f"Error: {e}")
        return False
    finally:
        close_connection(connection, cursor)


def blacklist_get_all():
    try:
        connection = create_connection()
        cursor = connection.cursor()

        select_blacklist_query = """
        SELECT word FROM blacklist;
        """

        cursor.execute(select_blacklist_query)
        words = cursor.fetchall()

        if words:
            return [word[0] for word in words]
        else:
            return []

    except mysql.connector.Error as e:
        print(f"Error: {e}")
        return []
    finally:
        close_connection(connection, cursor)


def clicks_check_is_fastest(time_to_check):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute("""
            SELECT MIN(time_taken)
            FROM leaderboard
            WHERE time_taken IS NOT NULL
        """)
        fastest_time_taken_data = cursor.fetchone()
        close_connection(connection, cursor)

        fastest_time_taken = fastest_time_taken_data[0] if fastest_time_taken_data else None
        if fastest_time_taken is None:
            return True
        elif isinstance(time_to_check, (int, float)) and isinstance(fastest_time_taken, (int, float)):
            if time_to_check < fastest_time_taken:
                return True
            else:
                return False
        else:
            return False
    except mysql.connector.Error:
        return False


def clicks_fastest_time():
    try:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute("""
            SELECT name, MIN(time_taken)
            FROM leaderboard
            WHERE time_taken = (SELECT MIN(time_taken) FROM leaderboard WHERE time_taken IS NOT NULL)
        """)
        fastest_time_taken_data = cursor.fetchone()
        close_connection(connection, cursor)
        return fastest_time_taken_data if fastest_time_taken_data else ("No user", 0)
    except mysql.connector.Error:
        return ("No user", 0)
    

def clicks_slowest_time():
    try:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute("""
            SELECT name, MAX(time_taken)
            FROM leaderboard
            WHERE time_taken = (SELECT MAX(time_taken) FROM leaderboard WHERE time_taken IS NOT NULL)
        """)
        slowest_time_taken_data = cursor.fetchone()
        close_connection(connection, cursor)
        return slowest_time_taken_data if slowest_time_taken_data else ("No user", 0)
    except mysql.connector.Error:
        return ("No user", 0)


def clicks_get_by_name(name):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute("""
            SELECT clicks, time_taken
            FROM leaderboard
            WHERE name = %s
        """, (name,))
        user_data = cursor.fetchone()
        close_connection(connection, cursor)
        return user_data if user_data else (0, 0)
    except mysql.connector.Error:
        return (0, 0)


def clicks_get_leaderboard(limit=None):
    try:
        if limit is None:
            limit = 10
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute("""
            SELECT name, clicks
            FROM leaderboard
            ORDER BY clicks DESC
            LIMIT %s
        """, (limit,))
        leaderboard_data = cursor.fetchall()
        leaderboard_text = ""
        for rank, (name, clicks) in enumerate(leaderboard_data, start=1):
            leaderboard_text += f"{rank} {name}: {clicks}\n"
        close_connection(connection, cursor)
        return leaderboard_text
    except mysql.connector.Error:
        return "Error retrieving leaderboard data"


def clicks_get_total():
    try:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute("""
            SELECT SUM(clicks)
            FROM leaderboard
        """)
        total_clicks = cursor.fetchone()
        close_connection(connection, cursor)
        return total_clicks[0] if total_clicks else 0
    except mysql.connector.Error:
        return 0


def clicks_reset():
    try:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM leaderboard")
        connection.commit()
        close_connection(connection, cursor)
        return "Leaderboard cleared successfully"
    except mysql.connector.Error:
        return "Error clearing leaderboard"


async def clicks_update(name, time_taken):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT clicks, time_taken
        FROM leaderboard
        WHERE name = %s
    """, (name,))
    user_data = cursor.fetchone()
    if user_data is None:
        cursor.execute("""
            INSERT INTO leaderboard (name, clicks, time_taken)
            VALUES (%s, 1, %s)
        """, (name, time_taken))
    else:
        clicks = user_data[0]
        current_time_taken = user_data[1]

        if current_time_taken is None or time_taken < current_time_taken:
            cursor.execute("""
                UPDATE leaderboard
                SET clicks = %s, time_taken = %s
                WHERE name = %s
            """, (clicks + 1, time_taken, name))
        else:
            cursor.execute("""
                UPDATE leaderboard
                SET clicks = %s, time_taken = %s
                WHERE name = %s
            """, (clicks + 1, current_time_taken, name))
    connection.commit()
    close_connection(connection, cursor)