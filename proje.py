from baglanti import create_connection
from PyQt5.QtWidgets import *
from datetime import datetime
from arayuz_ui import Ui_MainWindow
import sys

mydb = create_connection()

try:
    if mydb.is_connected():
        print("MySQL bağlantisi başarili!")
        cursor = mydb.cursor()
        cursor.execute("select * from projects")
        print("Tablolar:")
        for table in cursor.fetchall():
            print(table)
            
except Exception as e:
    print(f"Hata oluştu: {e}")
    

from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QMessageBox
from datetime import datetime

class MainApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainApp, self).__init__()
        self.setupUi(self)
        self.connection = mydb
        self.tabWidget.setCurrentIndex(0)
        self.populate_tableWidget()
        self.addProjeButton.clicked.connect(self.add_new_proje)
        self.deleteProjeButton.clicked.connect(self.delete_selected_project)
        self.editProjeButton.clicked.connect(self.edit_proje)
        self.populate_tableWidget_2()
        self.addEmployeeButton.clicked.connect(self.add_new_employee)
        self.deleteEmployeeButton.clicked.connect(self.delete_selected_employee)
        self.editEmployeeButton.clicked.connect(self.edit_employee)
        self.tableWidget.cellClicked.connect(self.project_clicked)
        self.addTaskButton.clicked.connect(self.add_new_task)
        self.deleteTaskButton.clicked.connect(self.delete_selected_task)
        self.editTaskButton.clicked.connect(lambda: self.edit_task(self.current_project_id))
        self.tableWidget_2.cellClicked.connect(self.employee_clicked)

    def populate_tableWidget(self):
        """Projeler tablosunu veritabanındaki projelerle doldurur."""
        try:
            # Veritabanından gecikme miktarını da sorguluyoruz
            qry = "SELECT project_id, project_name, start_date, end_date, delay_days FROM projects"
            cursor.execute(qry)
            results = cursor.fetchall()

            # Tabloyu temizle ve sütun başlıklarını ayarla
            self.tableWidget.clearContents()
            self.tableWidget.setRowCount(len(results))
            self.tableWidget.setColumnCount(5)  # 5 sütun: ID, Adı, Başlangıç Tarihi, Bitiş Tarihi, Gecikme
            self.tableWidget.setHorizontalHeaderLabels(["Project Id", "Project Name", "Start Date", "End Date", "Delay (Days)"])

            # Satırları tabloya ekle
            for row_idx, row_data in enumerate(results):
                for col_idx, col_data in enumerate(row_data):
                    self.tableWidget.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data) if col_data else "0"))
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error loading projects: {e}")

    def add_new_proje(self):
        row_count = self.tableWidget.rowCount()
        self.tableWidget.insertRow(row_count)
        for column in range(self.tableWidget.columnCount()):
            self.tableWidget.setItem(row_count, column, QTableWidgetItem(""))

    def delete_selected_project(self):
        """Seçili projeyi veritabanindan siler."""
        current_row = self.tableWidget.currentRow()
        if current_row == -1:
            QMessageBox.warning(self, "Hata", "Silmek için bir proje seçmelisiniz.")
            return

        project_id = self.tableWidget.item(current_row, 0).text()
        confirm = QMessageBox.question(self, "Silme Onayi", f"{project_id} projesini silmek istediğinizden emin misiniz?")
        if confirm == QMessageBox.Yes:
            try:
                qry = "DELETE FROM projects WHERE project_id = %s"
                cursor.execute(qry, (project_id,))
                mydb.commit()
                self.populate_tableWidget()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Database error while deleting: {e}")

    def edit_proje(self):
        """Projeleri düzenler ve veritabanina kaydeder."""
        for row in range(self.tableWidget.rowCount()):
            proje_id = project_name = self.tableWidget.item(row, 0).text() if self.tableWidget.item(row, 0) else ""
            project_name = self.tableWidget.item(row, 1).text() if self.tableWidget.item(row, 0) else ""
            start_date = self.tableWidget.item(row, 2).text() if self.tableWidget.item(row, 1) else ""
            end_date = self.tableWidget.item(row, 3).text() if self.tableWidget.item(row, 2) else ""

            if not project_name.strip():
                QMessageBox.warning(self, "Hata", f"Satir {row + 1}: Proje adi boş olamaz.")
                return

            if not self.is_valid_date(start_date) or not self.is_valid_date(end_date):
                QMessageBox.warning(self, "Hata", f"Satir {row + 2}: Tarihler uygun formatta değil (YYYY-MM-DD).")
                return

            try:
                qry = """
                    INSERT INTO projects (project_name, start_date, end_date)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        start_date = VALUES(start_date),
                        end_date = VALUES(end_date)
                """
                values = (project_name, start_date, end_date)
                cursor.execute(qry, values)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Database error while saving: {e}")
                return

        mydb.commit()
        QMessageBox.information(self, "Başarili", "Projeler başariyla kaydedildi/güncellendi!")
        self.populate_tableWidget()

    def populate_tableWidget_2(self):
        """Çalişan tablosonu veritabanindaki Çalişanlarla doldurur."""
        try:
            qry = "SELECT employee_id , full_name , hire_date FROM employees"
            cursor.execute(qry)
            results = cursor.fetchall()

            self.tableWidget_2.clearContents()
            self.tableWidget_2.setRowCount(len(results))
            self.tableWidget_2.setColumnCount(3)
            self.tableWidget_2.setHorizontalHeaderLabels(["Employee ID" ,"Employee Name", "Hire Date",])

            for row_idx, row_data in enumerate(results):
                for col_idx, col_data in enumerate(row_data):
                    self.tableWidget_2.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data) if col_data else ""))
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error loading projects: {e}")

    def add_new_employee(self):
        """Çalişanlar tablosuna yeni bir çalişan ekler (sadece tablo düzeyinde, veritabanina eklemez)."""
        row_count = self.tableWidget_2.rowCount()
        self.tableWidget_2.insertRow(row_count)
        for column in range(self.tableWidget_2.columnCount()):
            self.tableWidget_2.setItem(row_count, column, QTableWidgetItem(""))

    def delete_selected_employee(self):
        """Seçili çalişani veritabanindan siler."""
        current_row = self.tableWidget_2.currentRow()
        if current_row == -1:
            QMessageBox.warning(self, "Hata", "Silmek için bir çalişan seçmelisiniz.")
            return

        employee_ID = self.tableWidget_2.item(current_row, 0).text()
        confirm = QMessageBox.question(self, "Silme Onayi", f"{employee_ID} numarali çalişani silmek istediğinizden emin misiniz?")
        if confirm == QMessageBox.Yes:
            try:
                qry = "DELETE FROM employees WHERE employee_id = %s"
                cursor.execute(qry, (employee_ID,))
                mydb.commit()
                self.populate_tableWidget_2()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Database error while deleting: {e}")

    def edit_employee(self):
        """Çalişan bilgilerini günceller veya yeni çalişan ekler."""
        for row in range(self.tableWidget_2.rowCount()):
            # Satirdaki verileri al
            employee_ID = self.tableWidget_2.item(row, 0).text() if self.tableWidget_2.item(row, 0) else None
            full_name = self.tableWidget_2.item(row, 1).text() if self.tableWidget_2.item(row, 1) else ""
            hire_date = self.tableWidget_2.item(row, 2).text() if self.tableWidget_2.item(row, 2) else ""

            # Giriş doğrulamasi
            if not full_name.strip():
                QMessageBox.warning(self, "Hata", f"Satir {row + 1}: Çalişan adi boş olamaz.")
                return
            if not self.is_valid_date(hire_date):
                QMessageBox.warning(self, "Hata", f"Satir {row + 1}: Tarih uygun formatta değil (YYYY-MM-DD).")
                return

            try:
                if employee_ID:  # Mevcut çalişani güncelle
                    qry = """
                        UPDATE employees
                        SET full_name = %s, hire_date = %s
                        WHERE employee_id = %s
                    """
                    cursor.execute(qry, (full_name, hire_date, employee_ID))
                else:  # Yeni çalişan ekle
                    qry = """
                        INSERT INTO employees (full_name, hire_date)
                        VALUES (%s, %s)
                    """
                    cursor.execute(qry, (full_name, hire_date))

            except Exception as e:
                QMessageBox.warning(self, "Error", f"Database error while editing: {e}")
                return

        mydb.commit()
        QMessageBox.information(self, "Başarili", "Çalişan bilgileri başariyla kaydedildi/güncellendi!")
        self.populate_tableWidget_2()

    def project_clicked(self):
        """Projeye tıklandığında görevler sayfasına geçiş yapar."""
        current_row = self.tableWidget.currentRow()
        if current_row == -1:
            QMessageBox.warning(self, "Hata", "Lütfen bir proje seçin.")
            return

        project_id = self.tableWidget.item(current_row, 0).text()  # İlk sütun Project ID
        project_start_date = self.tableWidget.item(current_row, 2).text()  # Üçüncü sütun Start Date
        project_end_date = self.tableWidget.item(current_row , 3).text() #Dördüncü sütün End Date

        if not project_id or not project_start_date:
            QMessageBox.warning(self, "Hata", "Proje bilgisi eksik.")
            return

        self.current_project_id = project_id  # Proje ID'sini saklayın
        self.current_project_start_date = project_start_date  # Başlangıç tarihini saklayın
        self.current_project_end_date = project_end_date  # Bitiş tarihini saklayın
        print(f"Selected Project Start Date: {self.current_project_start_date}")  # Loglama

        self.populate_tableWidget_3(project_id)  # Görevleri doldurun
        self.tabWidget.setCurrentIndex(2)  # Görevler sekmesine geçin

    def populate_tableWidget_3(self, project_id):
        """Belirli bir projeye ait görevleri tablodan yükler."""
        try:
            qry = """
                SELECT task_id, task_name, start_date, end_date, adam_gun, status, employee_id
                FROM tasks
                WHERE project_id = %s
            """
            cursor.execute(qry, (project_id,))
            results = cursor.fetchall()

            self.tableWidget_3.clearContents()
            self.tableWidget_3.setRowCount(len(results))
            self.tableWidget_3.setColumnCount(7)
            self.tableWidget_3.setHorizontalHeaderLabels([
                "Task ID", "Task Name", "Start Date", "End Date", "Adam Gün", "Status", "Employee ID"
            ])

            for row_idx, row_data in enumerate(results):
                for col_idx, col_data in enumerate(row_data):
                    self.tableWidget_3.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data) if col_data else ""))
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Görevler yüklenirken bir hata oluştu: {e}")

    def add_new_task(self):
        """Tabloya yeni bir görev ekler (geçici)."""
        row_count = self.tableWidget_3.rowCount()
        self.tableWidget_3.insertRow(row_count)
        for column in range(self.tableWidget_3.columnCount()):
            self.tableWidget_3.setItem(row_count, column, QTableWidgetItem(""))

    def delete_selected_task(self, project_id):
        """Seçili görevi veritabanindan siler."""
        current_row = self.tableWidget_3.currentRow()
        if current_row == -1:
            QMessageBox.warning(self, "Hata", "Silmek için bir görev seçmelisiniz.")
            return

        task_ID = self.tableWidget_3.item(current_row, 0).text()
        confirm = QMessageBox.question(self, "Silme Onayi", f"{task_ID} numarali görevi silmek istediğinizden emin misiniz?")
        if confirm == QMessageBox.Yes:
            try:
                qry = "DELETE FROM tasks WHERE task_id = %s"
                cursor.execute(qry, (task_ID,))
                mydb.commit()
                self.populate_tableWidget_3(project_id)
            except Exception as e:
                QMessageBox.warning(self, "Hata", f"Görev silinirken bir hata oluştu: {e}")
                
    def determine_task_status(self,project_start_date, task_start_date, task_end_date):
        """Durum belirleme fonksiyonu."""
        today = datetime.now().date()  # Bugünün tarihi

        # Görev henüz başlamamışsa
        if today < project_start_date or today < task_start_date:
            return "Tamamlanacak"

        # Görev devam ediyorsa
        if task_end_date is None or today <= task_end_date:
            return "Devam Ediyor"

        # Görev tamamlanmışsa
        return "Tamamlandı"

    def edit_task(self, project_id):
        """Görev güncelleme veya yeni bir görevi kaydetme işlemi."""
        current_row = self.tableWidget_3.currentRow()
        if current_row == -1:
            QMessageBox.warning(self, "Hata", "Düzenlemek için bir görev seçmelisiniz.")
            return

        try:
            task_id = self.tableWidget_3.item(current_row, 0).text()  # İlk sütun Task ID
            task_name = self.tableWidget_3.item(current_row, 1).text() or ""
            start_date = self.tableWidget_3.item(current_row, 2).text() or ""
            end_date = self.tableWidget_3.item(current_row, 3).text() or None
            adam_gun = self.tableWidget_3.item(current_row, 4).text() or ""
            employee_id = self.tableWidget_3.item(current_row, 6).text()

            # Tarihleri datetime formatına çevir
            project_start_date = datetime.strptime(self.current_project_start_date, "%Y-%m-%d").date()
            project_end_date = datetime.strptime(self.current_project_end_date, "%Y-%m-%d").date()
            task_end_date = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None

            # Durumu belirle
            status = self.determine_task_status(project_start_date, datetime.strptime(start_date, "%Y-%m-%d").date(), task_end_date)

            # Görev güncelleme veya ekleme
            if task_id:  # Mevcut görev güncelleniyor
                qry = """
                    UPDATE tasks
                    SET task_name = %s, start_date = %s, end_date = %s, adam_gun = %s, status = %s, employee_id = %s
                    WHERE task_id = %s
                """
                values = (task_name, start_date, end_date, adam_gun, status, employee_id, task_id)
            else:  # Yeni görev ekleniyor
                qry = """
                    INSERT INTO tasks (project_id, task_name, start_date, end_date, adam_gun, status, employee_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                values = (project_id, task_name, start_date, end_date, adam_gun, status, employee_id)

            cursor.execute(qry, values)
            mydb.commit()

            # Proje bitiş tarihini kontrol et ve gerekirse güncelle
            if task_end_date and task_end_date > project_end_date:
                delay_days = (task_end_date - project_end_date).days
                update_project_qry = """
                    UPDATE projects
                    SET end_date = %s, delay_days = delay_days + %s
                    WHERE project_id = %s
                """
                update_values = (task_end_date, delay_days, project_id)
                cursor.execute(update_project_qry, update_values)
                mydb.commit()

            QMessageBox.information(self, "Başarılı", "Görev başarıyla kaydedildi/güncellendi!")
            self.populate_tableWidget_3(project_id)  # Görevler tablosunu yenile
            self.populate_tableWidget()  # Projeler tablosunu yenile
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Görev düzenlenirken bir hata oluştu: {e}")

    def employee_clicked(self):
        """çalişan tablosunda seçilen çalişanin detaylarinin gösteren sayfaya yonlendirilir"""
        current_row = self.tableWidget_2.currentRow()  # Çalişan tablosu
        if current_row == -1:
            QMessageBox.warning(self, "Hata", "Lütfen bir çalişan seçin.")
            return

        employee_id = self.tableWidget_2.item(current_row, 0).text()  # İlk sütun Employee ID
        if not employee_id:
            QMessageBox.warning(self, "Hata", "Çalişan bilgisi eksik.")
            return

        self.populate_tableWidget_4(employee_id)
        self.populate_tableWidget_5(employee_id)
        self.tabWidget.setCurrentIndex(3)  # Çalişan Detaylari sekmesine geç

    def populate_tableWidget_4(self, employee_id):
        """Çalışanın yer aldığı projeleri ve görevlerini doldurur."""
        try:
            qry = """
                SELECT p.project_name, t.task_name, t.status
                FROM projects p
                JOIN tasks t ON p.project_id = t.project_id
                WHERE t.employee_id = %s
            """
            cursor.execute(qry, (employee_id,))
            results = cursor.fetchall()

            self.tableWidget_4.clearContents()
            self.tableWidget_4.setRowCount(len(results))
            self.tableWidget_4.setColumnCount(3)
            self.tableWidget_4.setHorizontalHeaderLabels(["Proje Adı", "Görev Adı", "Durum"])

            for row_idx, row_data in enumerate(results):
                for col_idx, col_data in enumerate(row_data):
                    self.tableWidget_4.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Proje ve görevler yüklenirken bir hata oluştu: {e}")
            
    def populate_tableWidget_5(self, employee_id):
        """Çalışanın görev istatistiklerini doldurur."""
        try:
            qry = """
                SELECT 
                    COUNT(CASE 
                        WHEN DATE_ADD(t.start_date, INTERVAL t.adam_gun DAY) >= t.end_date THEN 1 
                        END) AS on_time,
                    COUNT(CASE 
                        WHEN DATE_ADD(t.start_date, INTERVAL t.adam_gun DAY) < t.end_date THEN 1 
                        END) AS late
                FROM tasks t
                WHERE t.employee_id = %s AND t.status = 'Tamamlandı'
            """
            cursor.execute(qry, (employee_id,))
            result = cursor.fetchone()

            self.tableWidget_5.clearContents()
            self.tableWidget_5.setRowCount(1)
            self.tableWidget_5.setColumnCount(2)
            self.tableWidget_5.setHorizontalHeaderLabels(["Zamanında Tamamlanan", "Zamanında Tamamlanamayan"])

            self.tableWidget_5.setItem(0, 0, QTableWidgetItem(str(result[0] or 0)))  # Zamanında Tamamlanan
            self.tableWidget_5.setItem(0, 1, QTableWidgetItem(str(result[1] or 0)))  # Zamanında Tamamlanamayan
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"İstatistikler yüklenirken bir hata oluştu: {e}")

    @staticmethod
    def is_valid_date(date_string):
        """Tarih formatini doğrular."""
        try:
            datetime.strptime(date_string, "%Y-%m-%d")
            return True
        except ValueError:
            return False

def main():
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    app.exec_()

if __name__ == "__main__":
    main()