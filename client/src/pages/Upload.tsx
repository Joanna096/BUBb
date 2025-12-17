import React, { useRef, useState } from 'react';
import { Layout } from '@/components/Layout';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Upload as UploadIcon, FileSpreadsheet, AlertCircle, CheckCircle } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { useVolunteers } from '@/context/VolunteerContext';
import * as XLSX from 'xlsx';
import { type Volunteer, type SkillType, type Availability } from '@/lib/data';
import { cn } from '@/lib/utils';

export default function Upload() {
  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { mergeVolunteers } = useVolunteers();

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const validateAndSetFile = (file: File) => {
    setError(null);
    setSuccess(null);
    
    const validTypes = [
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', // .xlsx
      'application/vnd.ms-excel', // .xls
      'text/csv' // .csv
    ];

    if (!validTypes.includes(file.type) && !file.name.endsWith('.xlsx') && !file.name.endsWith('.csv')) {
      setError('請上傳 Excel (.xlsx, .xls) 或 CSV 檔案');
      return;
    }

    setFile(file);
  };

  const handleUpload = async () => {
    if (!file) return;

    try {
      const data = await file.arrayBuffer();
      const workbook = XLSX.read(data);
      const worksheetName = workbook.SheetNames[0];
      const worksheet = workbook.Sheets[worksheetName];
      const jsonData = XLSX.utils.sheet_to_json(worksheet);

      if (jsonData.length === 0) {
        setError('檔案內容為空');
        return;
      }

      // Map Excel data to Volunteer interface
      // Expected headers: 姓名, 電話, LineID, 能力(逗號分隔), 時段(逗號分隔)
      const parsedVolunteers: Volunteer[] = jsonData.map((row: any) => {
        // Basic parsing logic - in a real app this would be more robust
        const skillsRaw = row['能力'] || row['Skills'] || '';
        const availabilityRaw = row['時段'] || row['Availability'] || '';

        const skills: { type: SkillType, level: number }[] = skillsRaw.split(/[,，]/).map((s: string) => {
          const trimmed = s.trim();
          // Default level 3 for imported skills
          return { type: trimmed as SkillType, level: 3 }; 
        }).filter((s: any) => s.type);

        const availability: Availability[] = availabilityRaw.split(/[,，]/).map((t: string) => t.trim() as Availability).filter((t: any) => t);

        return {
          id: Math.random().toString(), // Will be ignored if merging updates existing
          name: row['姓名'] || row['Name'] || '未命名',
          phone: row['電話'] || row['Phone'] || '',
          lineId: row['LineID'] || row['Line'] || '',
          skills: skills,
          availability: availability,
          trustMetrics: {
            punctuality: 80, // Default for new import
            taskCompletion: 3,
            reviews: 0
          },
          history: [],
          avatar: `https://api.dicebear.com/7.x/avataaars/svg?seed=${Math.random()}`
        };
      });

      mergeVolunteers(parsedVolunteers);
      setSuccess(`成功解析 ${parsedVolunteers.length} 筆資料並完成匯入！`);
      setFile(null);
    } catch (err) {
      console.error(err);
      setError('解析檔案時發生錯誤，請確認檔案格式正確');
    }
  };

  return (
    <Layout>
      <div className="space-y-6 animate-in fade-in duration-500 max-w-3xl mx-auto">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900">匯入志工資料</h1>
          <p className="text-slate-500 mt-1">批次上傳 Excel 或 CSV 檔案以更新志工池</p>
        </div>

        <Card className="border-none shadow-sm">
          <CardHeader>
            <CardTitle>檔案上傳</CardTitle>
            <CardDescription>
              支援 .xlsx, .xls, .csv 格式。系統將自動依據「姓名」與「電話」判斷是否為同一人。
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div 
              className={cn(
                "border-2 border-dashed rounded-lg p-12 text-center transition-colors cursor-pointer",
                isDragging ? "border-indigo-500 bg-indigo-50" : "border-slate-200 hover:border-indigo-300 hover:bg-slate-50",
                file ? "bg-emerald-50 border-emerald-200" : ""
              )}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              <input 
                type="file" 
                ref={fileInputRef} 
                className="hidden" 
                accept=".csv,.xlsx,.xls" 
                onChange={handleFileChange}
              />
              
              {file ? (
                <div className="flex flex-col items-center gap-2">
                  <FileSpreadsheet className="w-12 h-12 text-emerald-500" />
                  <p className="text-lg font-medium text-emerald-700">{file.name}</p>
                  <p className="text-sm text-emerald-600">{(file.size / 1024).toFixed(1)} KB</p>
                  <Button variant="ghost" size="sm" className="mt-2 text-emerald-700 hover:text-emerald-800 hover:bg-emerald-100" onClick={(e) => {
                    e.stopPropagation();
                    setFile(null);
                    setSuccess(null);
                    setError(null);
                  }}>
                    更換檔案
                  </Button>
                </div>
              ) : (
                <div className="flex flex-col items-center gap-2">
                  <UploadIcon className="w-12 h-12 text-slate-300" />
                  <p className="text-lg font-medium text-slate-600">點擊或拖曳檔案至此</p>
                  <p className="text-sm text-slate-400">Excel 欄位範例：姓名, 電話, LineID, 能力, 時段</p>
                </div>
              )}
            </div>

            {error && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertTitle>錯誤</AlertTitle>
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            {success && (
              <Alert className="bg-emerald-50 text-emerald-800 border-emerald-200">
                <CheckCircle className="h-4 w-4 text-emerald-600" />
                <AlertTitle>匯入成功</AlertTitle>
                <AlertDescription>{success}</AlertDescription>
              </Alert>
            )}

            <div className="flex justify-end">
              <Button 
                onClick={handleUpload} 
                disabled={!file}
                className="bg-indigo-600 hover:bg-indigo-700 text-white"
              >
                開始匯入
              </Button>
            </div>
            
            <div className="pt-4 border-t border-slate-100">
              <h4 className="text-sm font-semibold text-slate-700 mb-2">建議 Excel 格式範本：</h4>
              <div className="bg-slate-50 p-3 rounded text-xs font-mono text-slate-600 overflow-x-auto">
                <table className="w-full text-left">
                  <thead>
                    <tr className="border-b border-slate-200">
                      <th className="pb-1 pr-4">姓名</th>
                      <th className="pb-1 pr-4">電話</th>
                      <th className="pb-1 pr-4">LineID</th>
                      <th className="pb-1 pr-4">能力</th>
                      <th className="pb-1">時段</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td className="pt-1 pr-4">王小美</td>
                      <td className="pt-1 pr-4">0912345678</td>
                      <td className="pt-1 pr-4">may_wang</td>
                      <td className="pt-1 pr-4">行政,引導</td>
                      <td className="pt-1">平日晚,週末早</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
}
