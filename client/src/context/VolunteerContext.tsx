import React, { createContext, useContext, useState, ReactNode } from 'react';
import { MOCK_VOLUNTEERS, type Volunteer } from '@/lib/data';
import { useToast } from '@/hooks/use-toast';

interface VolunteerContextType {
  volunteers: Volunteer[];
  setVolunteers: React.Dispatch<React.SetStateAction<Volunteer[]>>;
  addRecord: (volunteerId: string, event: string, role: string) => void;
  mergeVolunteers: (newVolunteers: Volunteer[]) => void;
}

const VolunteerContext = createContext<VolunteerContextType | undefined>(undefined);

export function VolunteerProvider({ children }: { children: ReactNode }) {
  const [volunteers, setVolunteers] = useState<Volunteer[]>(MOCK_VOLUNTEERS);
  const { toast } = useToast();

  const addRecord = (volunteerId: string, event: string, role: string) => {
    setVolunteers(prev => prev.map(v => {
      if (v.id === volunteerId) {
        return {
          ...v,
          history: [...v.history, { 
            id: Math.random().toString(), 
            eventName: event, 
            role: role, 
            date: new Date().toISOString().split('T')[0] 
          }],
          trustMetrics: {
            ...v.trustMetrics,
            reviews: v.trustMetrics.reviews + 1
          }
        };
      }
      return v;
    }));
    toast({
      title: "紀錄已新增",
      description: "成功新增一筆活動參與紀錄",
    });
  };

  const mergeVolunteers = (newVolunteers: Volunteer[]) => {
    setVolunteers(prev => {
      const updatedVolunteers = [...prev];
      let addedCount = 0;
      let updatedCount = 0;

      newVolunteers.forEach(newV => {
        const existingIndex = updatedVolunteers.findIndex(
          v => v.name === newV.name && v.phone === newV.phone
        );

        if (existingIndex !== -1) {
          // Update existing
          updatedVolunteers[existingIndex] = {
            ...updatedVolunteers[existingIndex],
            ...newV,
            // Preserve ID and History if not provided in new data
            id: updatedVolunteers[existingIndex].id, 
            history: [
              ...updatedVolunteers[existingIndex].history,
              ...newV.history
            ],
            // Merge skills (simple strategy: union)
            skills: newV.skills.length > 0 ? newV.skills : updatedVolunteers[existingIndex].skills,
            // Keep existing metrics if new ones are default/empty
            trustMetrics: newV.trustMetrics.reviews > 0 ? newV.trustMetrics : updatedVolunteers[existingIndex].trustMetrics
          };
          updatedCount++;
        } else {
          // Add new
          updatedVolunteers.push({ ...newV, id: Math.random().toString() });
          addedCount++;
        }
      });

      toast({
        title: "匯入完成",
        description: `新增 ${addedCount} 筆，更新 ${updatedCount} 筆資料`,
      });

      return updatedVolunteers;
    });
  };

  return (
    <VolunteerContext.Provider value={{ volunteers, setVolunteers, addRecord, mergeVolunteers }}>
      {children}
    </VolunteerContext.Provider>
  );
}

export function useVolunteers() {
  const context = useContext(VolunteerContext);
  if (context === undefined) {
    throw new Error('useVolunteers must be used within a VolunteerProvider');
  }
  return context;
}
