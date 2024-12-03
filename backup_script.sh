#!/bin/bash

# ======= Настройки =======

# Настройки базы данных
DB_USER="db_user"              # Логин для базы данных
DB_PASSWORD="securepassword"   # Пароль для базы данных
DB_NAME="example_db"           # Имя базы данных

# Локальный каталог для резервных копий
BACKUP_DIR="/home/kali/backup" # Папка, где будут храниться резервные копии
BACKUP_FILE="backup_$(date +%Y%m%d%H%M%S).sql"  # Имя файла с текущей датой

# Настройки удалённого сервера
REMOTE_USER="backup_user"      # Логин на удалённом сервере
REMOTE_HOST="192.168.240.111"    # IP-адрес или имя хоста удалённого сервера
REMOTE_DIR="/home/backup_user/db_backups"  # Папка для резервных копий на удалённом сервере

# Лог-файл для записи действий
LOG_FILE="/home/kali/backup/backup.log"

# ======= Функции =======

# Логирование сообщений
log_message() {
    echo "$(date +'%Y-%m-%d %H:%M:%S') - $1" >> $LOG_FILE
}

# ======= Резервное копирование =======

# Проверяем, существует ли папка для резервных копий
if [ ! -d "$BACKUP_DIR" ]; then
    mkdir -p "$BACKUP_DIR"
    log_message "Создан каталог для резервных копий: $BACKUP_DIR"
fi

# Создание резервной копии базы данных
mysqldump -u $DB_USER -p$DB_PASSWORD $DB_NAME > "$BACKUP_DIR/$BACKUP_FILE"

if [ $? -eq 0 ]; then
    log_message "Резервная копия базы данных создана: $BACKUP_DIR/$BACKUP_FILE"
else
    log_message "Ошибка создания резервной копии базы данных!"
    exit 1
fi

# ======= Отправка на удалённый сервер =======

scp "$BACKUP_DIR/$BACKUP_FILE" "$REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR"

if [ $? -eq 0 ]; then
    log_message "Файл $BACKUP_FILE успешно отправлен на $REMOTE_HOST:$REMOTE_DIR"
else
    log_message "Ошибка отправки файла $BACKUP_FILE на удалённый сервер!"
    exit 1
fi

# ======= Очистка старых резервных копий =======

# Удаление локальных файлов старше 7 дней
find "$BACKUP_DIR" -type f -name "*.sql" -mtime +7 -exec rm {} \;

if [ $? -eq 0 ]; then
    log_message "Старые резервные копии удалены из $BACKUP_DIR"
else
    log_message "Ошибка удаления старых резервных копий!"
fi

# ======= Завершение =======
log_message "Скрипт успешно завершён."
exit 0
